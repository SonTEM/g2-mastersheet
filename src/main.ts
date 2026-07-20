import {
  waitForEvenAppBridge,
  type EvenAppBridge,
  TextContainerProperty,
  ImageContainerProperty,
  ImageRawDataUpdate,
  CreateStartUpPageContainer,
  OsEventTypeList,
} from '@evenrealities/even_hub_sdk'

type Manifest = { count: number; cards: string[][] }

const statusEl = document.querySelector<HTMLParagraphElement>('#status')!
const previewEl = document.querySelector<HTMLImageElement>('#cardPreview')!

function setStatus(text: string) {
  statusEl.textContent = text
}

// ---------------------------------------------------------------- tiles

const manifest: Manifest = await (await fetch(`${import.meta.env.BASE_URL}cards.json`)).json()
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
  // The full card = 4 tiles; previewing tile 0's card via the preview/ copy
  // isn't bundled, so stitch tiles on a canvas for the phone-side preview.
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
  // Plain-browser mode (no Even app): just preview cards, arrow keys flip.
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

  // Restore last position.
  try {
    const saved = await bridge.getLocalStorage('cardIdx')
    const n = parseInt(saved ?? '', 10)
    if (!Number.isNaN(n) && n >= 0 && n < manifest.count) idx = n
  } catch {
    /* first run */
  }

  // Full-screen text container behind the images captures all input
  // (image containers cannot set isEventCapture).
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

  // 2x2 grid of 288x144 image containers = full 576x288 canvas.
  const tilePos = [
    [0, 0],
    [288, 0],
    [0, 144],
    [288, 144],
  ]
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

  const created = await bridge.createStartUpPageContainer(
    new CreateStartUpPageContainer({
      containerTotalNum: 5,
      textObject: [eventLayer],
      imageObject,
    }),
  )
  if (created !== 0) {
    setStatus(`createStartUpPageContainer failed: ${created}`)
    return
  }

  await showCard(idx)
  setStatus(`On glasses — card ${idx + 1}/${manifest.count}. Phone can go in your pocket.`)

  // updateImageRawData must be serial: one in flight at a time. A newer
  // showCard() bumps `generation` so stale tile sends are skipped.
  async function showCard(target: number) {
    const gen = ++generation
    idx = target
    showPhonePreview(target)
    void bridge.setLocalStorage('cardIdx', String(target)).catch(() => {})
    queue = queue.then(async () => {
      for (let t = 0; t < 4; t++) {
        if (gen !== generation) return
        const bytes = await getTile(manifest.cards[target][t])
        if (gen !== generation) return
        const result = await bridge.updateImageRawData(
          new ImageRawDataUpdate({
            containerID: 2 + t,
            containerName: `tile${t}`,
            imageData: bytes,
          }),
        )
        if (String(result) !== 'success') console.error('updateImageRawData:', result)
      }
    })
    await queue
    prefetchCard(target + 1)
    prefetchCard(target - 1)
    setStatus(`On glasses — card ${target + 1}/${manifest.count}`)
  }

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
    // taps through sysEvent OR textEvent depending on the active container.
    const sysType = event.sysEvent?.eventType
    const textType = event.textEvent?.eventType

    if (
      sysType === OsEventTypeList.DOUBLE_CLICK_EVENT ||
      textType === OsEventTypeList.DOUBLE_CLICK_EVENT
    ) {
      // Root page: hand back to the host for the exit dialogue (required UX).
      void bridge.shutDownPageContainer(1)
      return
    }

    if (
      sysType === OsEventTypeList.FOREGROUND_ENTER_EVENT ||
      textType === OsEventTypeList.FOREGROUND_ENTER_EVENT
    ) {
      void showCard(idx) // re-paint after returning from dashboard/background
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

    const isClick = (t: number | undefined, envelope: unknown) =>
      envelope != null && (t === OsEventTypeList.CLICK_EVENT || t === undefined)
    if (isClick(sysType, event.sysEvent) || isClick(textType, event.textEvent)) {
      next()
    }
  })
}
