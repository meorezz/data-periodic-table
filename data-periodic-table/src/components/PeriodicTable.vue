<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import * as THREE from 'three'
import { CSS3DObject, CSS3DRenderer } from 'three/examples/jsm/renderers/CSS3DRenderer.js'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

const props = defineProps({
  user: { type: Object, required: true },
  headers: { type: Array, required: true },
  rows: { type: Array, required: true },
})

const emit = defineEmits(['sign-out'])
const viewport = ref(null)
const selectedElement = ref(null)
let camera
let scene
let renderer
let controls
let animationFrame
let resizeHandler
const objects = []
const targets = { table: [], sphere: [], helix: [], grid: [] }
const TABLE_COLUMNS = 20
const TABLE_ROWS = 10
const TABLE_CELL_WIDTH = 140
const TABLE_CELL_HEIGHT = 180
const GRID_LENGTH = 10
const GRID_HEIGHT = 4
const GRID_WIDTH = 5
const GRID_CELL_WIDTH = 400
const GRID_CELL_HEIGHT = 400
const GRID_CELL_DEPTH = 700
const HELIX_STRANDS = 2
const HELIX_RADIUS = 900
const HELIX_ANGLE_STEP = 0.22
const HELIX_AXIAL_STEP = 30

const elementRows = [
  ['H', 'Hydrogen', '1.008'], ['He', 'Helium', '4.003'], ['Li', 'Lithium', '6.94'], ['Be', 'Beryllium', '9.012'], ['B', 'Boron', '10.81'], ['C', 'Carbon', '12.011'], ['N', 'Nitrogen', '14.007'], ['O', 'Oxygen', '15.999'], ['F', 'Fluorine', '18.998'], ['Ne', 'Neon', '20.180'],
  ['Na', 'Sodium', '22.990'], ['Mg', 'Magnesium', '24.305'], ['Al', 'Aluminium', '26.982'], ['Si', 'Silicon', '28.085'], ['P', 'Phosphorus', '30.974'], ['S', 'Sulfur', '32.06'], ['Cl', 'Chlorine', '35.45'], ['Ar', 'Argon', '39.948'],
  ['K', 'Potassium', '39.098'], ['Ca', 'Calcium', '40.078'], ['Sc', 'Scandium', '44.956'], ['Ti', 'Titanium', '47.867'], ['V', 'Vanadium', '50.942'], ['Cr', 'Chromium', '52.00'], ['Mn', 'Manganese', '54.938'], ['Fe', 'Iron', '55.845'], ['Co', 'Cobalt', '58.933'], ['Ni', 'Nickel', '58.693'], ['Cu', 'Copper', '63.546'], ['Zn', 'Zinc', '65.38'], ['Ga', 'Gallium', '69.723'], ['Ge', 'Germanium', '72.630'], ['As', 'Arsenic', '74.922'], ['Se', 'Selenium', '78.971'], ['Br', 'Bromine', '79.904'], ['Kr', 'Krypton', '83.798'],
  ['Rb', 'Rubidium', '85.468'], ['Sr', 'Strontium', '87.62'], ['Y', 'Yttrium', '88.906'], ['Zr', 'Zirconium', '91.224'], ['Nb', 'Niobium', '92.906'], ['Mo', 'Molybdenum', '95.95'], ['Tc', 'Technetium', '98'], ['Ru', 'Ruthenium', '101.07'], ['Rh', 'Rhodium', '102.91'], ['Pd', 'Palladium', '106.42'], ['Ag', 'Silver', '107.87'], ['Cd', 'Cadmium', '112.41'], ['In', 'Indium', '114.82'], ['Sn', 'Tin', '118.71'], ['Sb', 'Antimony', '121.76'], ['Te', 'Tellurium', '127.60'], ['I', 'Iodine', '126.90'], ['Xe', 'Xenon', '131.29'],
  ['Cs', 'Caesium', '132.91'], ['Ba', 'Barium', '137.33'], ['La', 'Lanthanum', '138.91'], ['Ce', 'Cerium', '140.12'], ['Pr', 'Praseodymium', '140.91'], ['Nd', 'Neodymium', '144.24'], ['Pm', 'Promethium', '145'], ['Sm', 'Samarium', '150.36'], ['Eu', 'Europium', '151.96'], ['Gd', 'Gadolinium', '157.25'], ['Tb', 'Terbium', '158.93'], ['Dy', 'Dysprosium', '162.50'], ['Ho', 'Holmium', '164.93'], ['Er', 'Erbium', '167.26'], ['Tm', 'Thulium', '168.93'], ['Yb', 'Ytterbium', '173.05'], ['Lu', 'Lutetium', '174.97'], ['Hf', 'Hafnium', '178.49'], ['Ta', 'Tantalum', '180.95'], ['W', 'Tungsten', '183.84'], ['Re', 'Rhenium', '186.21'], ['Os', 'Osmium', '190.23'], ['Ir', 'Iridium', '192.22'], ['Pt', 'Platinum', '195.08'], ['Au', 'Gold', '196.97'], ['Hg', 'Mercury', '200.59'], ['Tl', 'Thallium', '204.38'], ['Pb', 'Lead', '207.2'], ['Bi', 'Bismuth', '208.98'], ['Po', 'Polonium', '209'], ['At', 'Astatine', '210'], ['Rn', 'Radon', '222'],
  ['Fr', 'Francium', '223'], ['Ra', 'Radium', '226'], ['Ac', 'Actinium', '227'], ['Th', 'Thorium', '232.04'], ['Pa', 'Protactinium', '231.04'], ['U', 'Uranium', '238.03'], ['Np', 'Neptunium', '237'], ['Pu', 'Plutonium', '244'], ['Am', 'Americium', '243'], ['Cm', 'Curium', '247'], ['Bk', 'Berkelium', '247'], ['Cf', 'Californium', '251'], ['Es', 'Einsteinium', '252'], ['Fm', 'Fermium', '257'], ['Md', 'Mendelevium', '258'], ['No', 'Nobelium', '259'], ['Lr', 'Lawrencium', '266'], ['Rf', 'Rutherfordium', '267'], ['Db', 'Dubnium', '268'], ['Sg', 'Seaborgium', '269'], ['Bh', 'Bohrium', '270'], ['Hs', 'Hassium', '277'], ['Mt', 'Meitnerium', '278'], ['Ds', 'Darmstadtium', '281'], ['Rg', 'Roentgenium', '282'], ['Cn', 'Copernicium', '285'], ['Nh', 'Nihonium', '286'], ['Fl', 'Flerovium', '289'], ['Mc', 'Moscovium', '290'], ['Lv', 'Livermorium', '293'], ['Ts', 'Tennessine', '294'], ['Og', 'Oganesson', '294'],
]

const nobleGases = new Set([2, 10, 18, 36, 54, 86, 118])
const nonMetals = new Set([1, 6, 7, 8, 9, 15, 16, 17, 35, 53])
const metalloids = new Set([5, 14, 32, 33, 51, 52, 84])
const lanthanides = new Set(Array.from({ length: 15 }, (_, index) => index + 58))
const actinides = new Set(Array.from({ length: 15 }, (_, index) => index + 90))

function category(number) {
  if (nobleGases.has(number)) return 'noble-gas'
  if (lanthanides.has(number)) return 'lanthanide'
  if (actinides.has(number)) return 'actinide'
  if (nonMetals.has(number)) return 'nonmetal'
  if (metalloids.has(number)) return 'metalloid'
  return 'metal'
}

function position(number) {
  const starts = [1, 3, 11, 19, 37, 55, 87]
  const period = starts.findLastIndex((start) => number >= start) + 1
  const offset = number - starts[period - 1]
  const lengths = [2, 8, 8, 18, 18, 32, 32]
  let group = offset + 1
  if (period === 2 || period === 3) group = offset === 0 ? 1 : offset + 11
  if (period >= 6 && offset >= 2) group = offset === 2 ? 3 : offset - 13
  if (lanthanides.has(number)) return { group: number - 54, row: 8 }
  if (actinides.has(number)) return { group: number - 86, row: 9 }
  return { group, row: period }
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  }[character]))
}

function getValue(values, field) {
  const key = Object.keys(values).find((candidate) => candidate.trim().toLowerCase() === field.toLowerCase())
  return key ? values[key] : ''
}

function parseNetWorth(value) {
  const normalized = String(value ?? '').replace(/[$,\s]/g, '').toUpperCase()
  const amount = Number.parseFloat(normalized)
  if (!Number.isFinite(amount)) return 0
  if (normalized.endsWith('M')) return amount * 1_000_000
  if (normalized.endsWith('K')) return amount * 1_000
  return amount
}

function createElement(number, chemicalData, row, headers) {
  const values = Object.fromEntries(headers.map((header, index) => [header, row?.[index] ?? '']))
  const [symbol, chemicalName, weight] = chemicalData
  const name = getValue(values, 'name') || chemicalName
  const photo = getValue(values, 'photo')
  const netWorth = parseNetWorth(getValue(values, 'net worth'))
  const netWorthClass = netWorth < 100_000 ? 'net-worth-low' : netWorth < 200_000 ? 'net-worth-medium' : 'net-worth-high'
  const details = headers
    .filter((header) => !['name', 'photo'].includes(header.trim().toLowerCase()))
    .map((header) => `<small>${escapeHtml(header)}: ${escapeHtml(values[header])}</small>`)
    .join('')
  const element = document.createElement('button')
  element.className = `element ${category(number)}`
  element.type = 'button'
  element.innerHTML = `
    <span class="chemical-content">
      <span class="number">${number}</span>
      <strong>${escapeHtml(symbol)}</strong>
      <span>${escapeHtml(chemicalName)}</span>
      <small>${escapeHtml(weight)}</small>
    </span>
    <span class="sheet-content ${netWorthClass}">
      ${photo ? `<img src="${escapeHtml(photo)}" alt="" />` : ''}
      <strong>${escapeHtml(name)}</strong>
      ${details}
    </span>`
  element.addEventListener('click', () => { selectedElement.value = { number, values, name } })
  return new CSS3DObject(element)
}

function makeTargets(object, number) {
  const { group, row } = position(number)
  const table = new THREE.Object3D()
  table.position.x = (group - (TABLE_COLUMNS + 1) / 2) * TABLE_CELL_WIDTH
  table.position.y = -(row - (TABLE_ROWS + 1) / 2) * TABLE_CELL_HEIGHT
  targets.table.push(table)

  const sphere = new THREE.Object3D()
  const phi = Math.acos(-1 + (2 * number) / 118)
  const theta = Math.sqrt(118 * Math.PI) * phi
  sphere.position.setFromSphericalCoords(900, phi, theta)
  const vector = new THREE.Vector3().copy(sphere.position).multiplyScalar(2)
  sphere.lookAt(vector)
  targets.sphere.push(sphere)

  const helix = new THREE.Object3D()
  const helixIndex = number - 1
  const strand = helixIndex % HELIX_STRANDS
  const strandIndex = Math.floor(helixIndex / HELIX_STRANDS)
  const angle = strandIndex * HELIX_ANGLE_STEP + strand * Math.PI
  helix.position.setFromCylindricalCoords(
    HELIX_RADIUS,
    angle,
    (strandIndex - 29) * HELIX_AXIAL_STEP,
  )
  const helixVector = new THREE.Vector3().copy(helix.position)
  helix.lookAt(helixVector.multiplyScalar(2))
  targets.helix.push(helix)

  const grid = new THREE.Object3D()
  const gridIndex = number - 1
  const gridColumn = gridIndex % GRID_WIDTH
  const gridRow = Math.floor(gridIndex / GRID_WIDTH) % GRID_HEIGHT
  const gridLayer = Math.floor(gridIndex / (GRID_WIDTH * GRID_HEIGHT))
  grid.position.x = (gridColumn - (GRID_WIDTH - 1) / 2) * GRID_CELL_WIDTH
  grid.position.y = ((GRID_HEIGHT - 1) / 2 - gridRow) * GRID_CELL_HEIGHT
  grid.position.z = ((GRID_LENGTH - 1) / 2 - gridLayer) * GRID_CELL_DEPTH
  targets.grid.push(grid)
  object.position.set(0, 0, 0)
}

function transform(name) {
  const duration = 2000
  const start = performance.now()
  const from = objects.map((object) => ({
    position: object.position.clone(),
    quaternion: object.quaternion.clone(),
  }))
  const to = targets[name]
  function animateTransform(now) {
    const progress = Math.min((now - start) / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    objects.forEach((object, index) => {
      object.position.lerpVectors(from[index].position, to[index].position, eased)
      object.quaternion.slerpQuaternions(from[index].quaternion, to[index].quaternion, eased)
    })
    if (progress < 1) requestAnimationFrame(animateTransform)
  }
  requestAnimationFrame(animateTransform)
}

onMounted(() => {
  const width = viewport.value.clientWidth
  const height = viewport.value.clientHeight
  camera = new THREE.PerspectiveCamera(40, width / height, 1, 10000)
  camera.position.z = 3000
  scene = new THREE.Scene()
  elementRows.forEach((chemicalData, index) => {
    const object = createElement(index + 1, chemicalData, props.rows[index], props.headers)
    objects.push(object)
    scene.add(object)
    makeTargets(object, index + 1)
  })
  renderer = new CSS3DRenderer()
  renderer.setSize(width, height)
  viewport.value.appendChild(renderer.domElement)
  controls = new OrbitControls(camera, renderer.domElement)
  controls.minDistance = 500
  controls.maxDistance = 6000
  controls.addEventListener('change', () => renderer.render(scene, camera))
  resizeHandler = () => {
    const nextWidth = viewport.value.clientWidth
    const nextHeight = viewport.value.clientHeight
    camera.aspect = nextWidth / nextHeight
    camera.updateProjectionMatrix()
    renderer.setSize(nextWidth, nextHeight)
    renderer.render(scene, camera)
  }
  window.addEventListener('resize', resizeHandler)
  transform('table')
  renderer.render(scene, camera)
  animationFrame = requestAnimationFrame(function renderLoop() {
    renderer.render(scene, camera)
    animationFrame = requestAnimationFrame(renderLoop)
  })
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animationFrame)
  window.removeEventListener('resize', resizeHandler)
  controls?.dispose()
  renderer?.domElement.remove()
})
</script>

<template>
  <div class="periodic-page">
    <header class="header">
      <div class="profile">
        <img :src="user.picture" alt="" class="avatar" referrerpolicy="no-referrer" />
        <div><strong>{{ user.name }}</strong><div class="email">{{ user.email }}</div></div>
      </div>
      <button class="sign-out" @click="emit('sign-out')">Sign out</button>
    </header>
    <div class="toolbar">
      <div><h1>Periodic Table</h1><p>Explore the elements in 3D</p></div>
    </div>
    <div ref="viewport" class="viewport"></div>
    <div class="views">
      <button v-for="view in ['table', 'sphere', 'helix', 'grid']" :key="view" @click="transform(view)">{{ view }}</button>
      <span class="legend">
        <span>LOW</span>
        <i class="legend-bar"></i>
        <span>HIGH</span>
      </span>
    </div>
    <aside v-if="selectedElement" class="details">
      <button class="close" aria-label="Close element details" @click="selectedElement = null">×</button>
      <span class="detail-number">#{{ selectedElement.number }}</span>
      <strong>{{ selectedElement.name }}</strong>
      <p v-for="(value, key) in selectedElement.values" :key="key">{{ key }}: {{ value }}</p>
    </aside>
  </div>
</template>

<style scoped>
.periodic-page { width: 100%; min-height: 100vh; padding: 22px 28px; box-sizing: border-box; background: radial-gradient(circle at 50% 35%, #20283e, #0d111b 70%); color: #eef2ff; overflow: hidden; }
.header, .toolbar { display: flex; align-items: center; justify-content: space-between; gap: 20px; }
.header { padding-bottom: 18px; border-bottom: 1px solid #30394f; }
.profile { display: flex; align-items: center; gap: 12px; text-align: left; }
.avatar { width: 40px; height: 40px; border-radius: 50%; }
.email, .toolbar p { color: #9da8c2; font-size: 12px; margin: 3px 0 0; }
.sign-out, .views button { border: 1px solid #485572; border-radius: 7px; padding: 8px 14px; color: #dce5ff; background: #182137; cursor: pointer; text-transform: capitalize; }
.toolbar { align-items: flex-start; padding: 20px 0 10px; }
.toolbar > div { text-align: left; }
h1 { margin: 0; color: #fff; font-size: 26px; }
.toolbar p { margin: 4px 0 0; line-height: 1.4; }
.views { display: flex; justify-content: center; gap: 7px; padding-top: 10px; }
.views button:hover, .sign-out:hover { background: #263453; }
.viewport { position: relative; height: min(70vh, 720px); min-height: 480px; }
:global(.element) { width: 120px; height: 160px; padding: 10px; box-sizing: border-box; border: 1px solid #008b8b; border-radius: 10px; color: white; text-align: left; cursor: pointer; font-family: inherit; background: #005b5b; box-shadow: 0 0 18px rgba(0, 139, 139, .22); transition: box-shadow .2s, transform .2s; }
:global(.chemical-content) { display: block; }
:global(.sheet-content) { position: absolute; inset: 0; z-index: 1; display: flex; flex-direction: column; justify-content: center; padding: 8px; box-sizing: border-box; opacity: 0; overflow: hidden; text-align: center; transition: opacity .15s ease; }
:global(.element:hover .sheet-content) { opacity: 1; }
:global(.sheet-content img) { width: 48px; height: 48px; margin: 0 auto 5px; border-radius: 50%; object-fit: cover; }
:global(.sheet-content strong) { display: block; max-height: 30px; overflow: hidden; font-size: 13px; line-height: 1.05; text-overflow: ellipsis; }
:global(.sheet-content small) { display: block; overflow: hidden; margin-top: 3px; font-size: 9px; line-height: 1.05; text-overflow: ellipsis; white-space: nowrap; }
:global(.sheet-content.net-worth-low) { background: rgba(65, 18, 18, .98); border: 2px solid #be2d2d; }
:global(.sheet-content.net-worth-medium) { background: rgba(62, 53, 12, .98); border: 2px solid #d5c51f; }
:global(.sheet-content.net-worth-high) { background: rgba(12, 55, 27, .98); border: 2px solid #2a8b4c; }
:global(.element:hover) { box-shadow: 0 0 24px rgba(160, 210, 255, .7); }
:global(.element strong) { display: block; margin-top: 20px; font-size: 38px; line-height: 1; text-align: center; }
:global(.element span:not(.number)), :global(.element small) { display: block; text-align: center; }
:global(.element span:not(.number)) { margin-top: 8px; font-size: 12px; }
:global(.element small) { margin-top: 9px; color: #b7c8ec; }
:global(.number) { float: right; font-size: 11px; }
:global(.element .sheet-content) { margin-top: 0; font-size: initial; }
:global(.element .sheet-content strong) { margin-top: 0; font-size: 13px; }
:global(.element .sheet-content small) { margin-top: 3px; color: white; }
:global(.metal) { background: #005b5b; }
:global(.nonmetal) { background: #006d6d; }
:global(.noble-gas) { background: #004848; }
:global(.metalloid) { background: #006363; }
:global(.lanthanide), :global(.actinide) { background: #005252; }
.details { position: fixed; right: 40px; bottom: 40px; width: 220px; padding: 20px; border: 1px solid #52658c; border-radius: 12px; background: rgba(14, 22, 38, .95); box-shadow: 0 10px 30px #0008; }
.legend { display: flex; align-items: center; gap: 5px; margin-left: 14px; padding: 3px 5px; color: #fff; font-size: 9px; }
.legend-bar { width: 92px; height: 7px; border: 1px solid #fff; background: linear-gradient(90deg, #e53935 0%, #ff8c2f 30%, #ffe52f 55%, #9bd438 78%, #2a8b4c 100%); }
.details strong { display: block; font-size: 48px; color: #9cc4ff; }.details h2 { margin: 4px 0; color: #fff; font-size: 20px; }.details p { color: #b5c1d9; font-size: 13px; }.detail-number { color: #91a1c2; font-size: 12px; }.close { float: right; border: 0; background: none; color: #fff; font-size: 24px; cursor: pointer; }
@media (max-width: 700px) { .periodic-page { padding: 16px; border-radius: 0; min-height: 100vh; }.toolbar { align-items: flex-start; flex-direction: column; }.views { flex-wrap: wrap; }.viewport { min-height: 430px; height: 62vh; }.details { right: 16px; bottom: 16px; }.element { width: 100px; height: 140px; } }
</style>
