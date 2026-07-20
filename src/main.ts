import {
  waitForEvenAppBridge,
  type EvenAppBridge,
  TextContainerProperty,
  ImageContainerProperty,
  ListContainerProperty,
  ListItemContainerProperty,
  ImageRawDataUpdate,
  CreateStartUpPageContainer,
  RebuildPageContainer,
  TextContainerUpgrade,
  OsEventTypeList,
} from '@evenrealities/even_hub_sdk'

type Manifest = { count: number; cards: string[][] }

const statusEl = document.querySelector<HTMLParagraphElement>('#status')!
const previewEl = document.querySelector<HTMLImageElement>('#cardPreview')!

function setStatus(text: string) {
  statusEl.textContent = text
}

// ---------------------------------------------------------------- tiles

// cards.json must never be served stale: a cached manifest references
// tile hashes that no longer exist after a redeploy (-> 404 -> blank).
// Tiles themselves are content-hashed, so caching them is always safe.
const manifest: Manifest = await (
  await fetch(`${import.meta.env.BASE_URL}cards.json?v=${Date.now()}`, { cache: 'no-store' })
).json()
const tileCache = new Map<string, Uint8Array>()

async function getTile(rel: string): Promise<Uint8Array> {
  const cached = tileCache.get(rel)
  if (cached) return cached
  const res = await fetch(`${import.meta.env.BASE_URL}${rel}`)
  if (!res.ok) throw new Error(`tile fetch failed: ${rel} ${res.status}`)
  const bytes = new Uint8Array(await res.arrayBuffer())
  tileCache.set(rel, bytes)
  return bytes
}

function prefetchCard(idx: number) {
  if (idx < 0 || idx >= manifest.count) return
  for (const rel of manifest.cards[idx]) void getTile(rel).catch(() => {})
}

let previewGen = 0
function showPhonePreview(idx: number) {
  const gen = ++previewGen
  void (async () => {
    const canvas = document.createElement('canvas')
    canvas.width = 576
    canvas.height = 288
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    const boxes = [
      [0, 0],
      [288, 0],
      [0, 144],
      [288, 144],
    ]
    for (let t = 0; t < 4; t++) {
      const bytes = await getTile(manifest.cards[idx][t])
      const bmp = await createImageBitmap(new Blob([bytes.buffer as ArrayBuffer], { type: 'image/png' }))
      ctx.drawImage(bmp, boxes[t][0], boxes[t][1])
    }
    if (gen === previewGen) previewEl.src = canvas.toDataURL('image/png')
  })()
}

// ---------------------------------------------------------------- bridge

// Inside the Even app the page runs in a flutter_inappwebview; a plain
// browser lacks the native handler, and the SDK's bridge object resolves
// anyway but every call fails — so detect the host, not the bridge.
const insideEvenApp = typeof (window as unknown as Record<string, unknown>).flutter_inappwebview !== 'undefined'

const bridge: EvenAppBridge | null = insideEvenApp ? await waitForEvenAppBridge() : null

let idx = 0
let generation = 0
let queue: Promise<void> = Promise.resolve()

if (!bridge) {
  setStatus('No glasses bridge found — browser preview mode.')
  showPhonePreview(idx)
  window.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight') idx = Math.min(idx + 1, manifest.count - 1)
    else if (e.key === 'ArrowLeft') idx = Math.max(idx - 1, 0)
    else return
    showPhonePreview(idx)
  })
} else {
  await startGlassesApp(bridge)
}

async function startGlassesApp(bridge: EvenAppBridge) {
  setStatus('Connected — building page…')

  // Section jump menu (opened with double-tap on a card).
  const SECTIONS: { label: string; target: number | 'exit' }[] = [
    { label: 'Start', target: 0 },
    { label: '1-2 Dimensions & pivots', target: 1 },
    { label: '3-4 Consistency & rank', target: 6 },
    { label: '5-6 Homogeneous & IMT', target: 10 },
    { label: '7 One-to-one & kernel', target: 16 },
    { label: '8 Linearity', target: 20 },
    { label: '9 Standard matrices', target: 22 },
    { label: '10 Composition', target: 27 },
    { label: 'Exam recipes', target: 29 },
    { label: 'Exit app', target: 'exit' },
  ]
  let mode: 'cards' | 'menu' = 'cards'

  try {
    const saved = await bridge.getLocalStorage('cardIdx')
    const n = parseInt(saved ?? '', 10)
    if (!Number.isNaN(n) && n >= 0 && n < manifest.count) idx = n
  } catch {
    /* first run */
  }

  const tilePos = [
    [0, 0],
    [288, 0],
    [0, 144],
    [288, 144],
  ]

  // Full-screen text container behind the images captures all input
  // (image containers cannot set isEventCapture).
  function cardContainers() {
    const eventLayer = new TextContainerProperty({
      xPosition: 0,
      yPosition: 0,
      width: 576,
      height: 288,
      borderWidth: 0,
      borderColor: 0,
      paddingLength: 0,
      containerID: 1,
      containerName: 'evt',
      content: ' ',
      isEventCapture: 1,
    })
    const counter = new TextContainerProperty({
      xPosition: 496,
      yPosition: 2,
      width: 78,
      height: 30,
      borderWidth: 0,
      borderColor: 0,
      paddingLength: 0,
      containerID: 6,
      containerName: 'counter',
      content: `${idx + 1}/${manifest.count}`,
      isEventCapture: 0,
    })
    const imageObject = tilePos.map(
      ([x, y], t) =>
        new ImageContainerProperty({
          xPosition: x,
          yPosition: y,
          width: 288,
          height: 144,
          containerID: 2 + t,
          containerName: `tile${t}`,
        }),
    )
    return { containerTotalNum: 6, textObject: [eventLayer, counter], imageObject }
  }

  function menuContainers() {
    const list = new ListContainerProperty({
      xPosition: 0,
      yPosition: 0,
      width: 576,
      height: 288,
      borderWidth: 0,
      borderColor: 5,
      borderRadius: 0,
      paddingLength: 4,
      containerID: 20,
      containerName: 'menu',
      isEventCapture: 1,
      itemContainer: new ListItemContainerProperty({
        itemCount: SECTIONS.length,
        itemWidth: 560,
        isItemSelectBorderEn: 1,
        itemName: SECTIONS.map(s => s.label),
      }),
    })
    return { containerTotalNum: 1, listObject: [list] }
  }

  const created = await bridge.createStartUpPageContainer(
    new CreateStartUpPageContainer(cardContainers()),
  )
  if (created !== 0) {
    setStatus(`createStartUpPageContainer failed: ${created}`)
    return
  }

  // updateImageRawData must be serial: one in flight at a time. A newer
  // showCard() bumps `generation` so stale tile sends are skipped. Tiles
  // already on screen are not re-sent — the wire cost is the decoded
  // 4-bit bitmap (~21KB/tile), not the PNG. Every queue link catches its
  // own errors so one failed send can never poison the chain.
  const onScreen: (string | null)[] = [null, null, null, null]
  async function showCard(target: number, force = false) {
    const gen = ++generation
    idx = target
    showPhonePreview(target)
    void bridge.setLocalStorage('cardIdx', String(target)).catch(() => {})
    void bridge
      .textContainerUpgrade(
        new TextContainerUpgrade({
          containerID: 6,
          containerName: 'counter',
          content: `${target + 1}/${manifest.count}`,
        }),
      )
      .catch(() => {})
    queue = queue.then(async () => {
      try {
        for (let t = 0; t < 4; t++) {
          if (gen !== generation || mode !== 'cards') return
          const rel = manifest.cards[target][t]
          if (!force && onScreen[t] === rel) continue
          const bytes = await getTile(rel)
          if (gen !== generation || mode !== 'cards') return
          const result = await bridge.updateImageRawData(
            new ImageRawDataUpdate({
              containerID: 2 + t,
              containerName: `tile${t}`,
              imageData: bytes,
            }),
          )
          if (String(result) === 'success') onScreen[t] = rel
          else console.error('updateImageRawData:', result)
        }
      } catch (err) {
        console.error('tile send failed', err)
        setStatus(`Tile send failed (card ${target + 1}): ${err instanceof Error ? err.message : err}`)
      }
    })
    await queue
    prefetchCard(target + 1)
    prefetchCard(target - 1)
    setStatus(`On glasses — card ${target + 1}/${manifest.count}`)
  }

  async function openMenu() {
    mode = 'menu'
    generation++ // abandon in-flight tile sends
    await bridge.rebuildPageContainer(new RebuildPageContainer(menuContainers())).catch(err => {
      console.error('menu rebuild failed', err)
    })
    setStatus('Menu open — click a section on the glasses.')
  }

  async function backToCards(target: number) {
    mode = 'cards'
    onScreen.fill(null) // containers were destroyed by the rebuild
    await bridge.rebuildPageContainer(new RebuildPageContainer(cardContainers())).catch(err => {
      console.error('card rebuild failed', err)
    })
    void showCard(target, true)
  }

  await showCard(idx)
  setStatus(`On glasses — card ${idx + 1}/${manifest.count}. Phone can go in your pocket.`)

  const next = () => void showCard(idx + 1 < manifest.count ? idx + 1 : 0)
  const prev = () => void showCard(idx - 1 >= 0 ? idx - 1 : manifest.count - 1)

  let lastScroll = 0
  function onScroll(direction: 'top' | 'bottom') {
    const now = Date.now()
    if (now - lastScroll < 350) return
    lastScroll = now
    direction === 'bottom' ? next() : prev()
  }

  bridge.onEvenHubEvent(event => {
    // Protobuf omits zero-value fields, so CLICK_EVENT (0) can arrive as
    // an envelope whose eventType is undefined. Real hardware may route
    // events through sysEvent, textEvent or listEvent depending on the
    // active container.
    const sysType = event.sysEvent?.eventType
    const textType = event.textEvent?.eventType
    const listType = event.listEvent?.eventType
    const isClick = (t: number | undefined, envelope: unknown) =>
      envelope != null && (t === OsEventTypeList.CLICK_EVENT || t === undefined)
    const doubleTap =
      sysType === OsEventTypeList.DOUBLE_CLICK_EVENT ||
      textType === OsEventTypeList.DOUBLE_CLICK_EVENT ||
      listType === OsEventTypeList.DOUBLE_CLICK_EVENT
    const foreground =
      sysType === OsEventTypeList.FOREGROUND_ENTER_EVENT ||
      textType === OsEventTypeList.FOREGROUND_ENTER_EVENT

    if (foreground) {
      // Full re-paint: containers may have been cleared by the host.
      if (mode === 'menu') void openMenu()
      else void backToCards(idx)
      return
    }

    if (mode === 'menu') {
      if (doubleTap) {
        void bridge.shutDownPageContainer(1)
        return
      }
      if (event.listEvent && isClick(listType, event.listEvent)) {
        const sel = event.listEvent.currentSelectItemIndex ?? 0
        const section = SECTIONS[sel]
        if (!section) return
        if (section.target === 'exit') void bridge.shutDownPageContainer(1)
        else void backToCards(section.target)
      }
      return
    }

    // cards mode
    if (doubleTap) {
      void openMenu()
      return
    }
    if (
      sysType === OsEventTypeList.SCROLL_BOTTOM_EVENT ||
      textType === OsEventTypeList.SCROLL_BOTTOM_EVENT
    ) {
      onScroll('bottom')
      return
    }
    if (
      sysType === OsEventTypeList.SCROLL_TOP_EVENT ||
      textType === OsEventTypeList.SCROLL_TOP_EVENT
    ) {
      onScroll('top')
      return
    }
    if (isClick(sysType, event.sysEvent) || isClick(textType, event.textEvent)) {
      next()
    }
  })
}
