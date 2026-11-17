// Общая «песочница» для прогонов .sb3 без браузера: jsdom, заглушки canvas
// и рендерера, загрузка проекта, клавиши и чтение переменных.
//
//   const {boot} = require('./vm_env');
//   const {vm, errors, frames, key, vars, backdropName, costumes, clones} = boot();
//
const {JSDOM} = require('jsdom');

const dom = new JSDOM('<!doctype html><html><body></body></html>', {pretendToBeVisual: true});
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;
global.DOMParser = dom.window.DOMParser;
global.XMLSerializer = dom.window.XMLSerializer;
global.Image = dom.window.Image;

function makeCanvas (w = 0, h = 0) {
    const ctx = {
        canvas: null,
        drawImage: () => {}, clearRect: () => {}, fillRect: () => {},
        getImageData: (x, y, wd, ht) => ({
            data: new Uint8ClampedArray(Math.max(4, Math.max(1, wd * ht * 4))),
            width: wd, height: ht
        }),
        putImageData: () => {},
        createImageData: (wd, ht) => ({data: new Uint8ClampedArray(Math.max(4, wd * ht * 4))}),
        save: () => {}, restore: () => {}, beginPath: () => {}, closePath: () => {},
        moveTo: () => {}, lineTo: () => {}, arc: () => {}, rect: () => {},
        fill: () => {}, stroke: () => {}, translate: () => {}, scale: () => {},
        rotate: () => {}, setTransform: () => {}, measureText: () => ({width: 10}),
        fillText: () => {}, strokeText: () => {}
    };
    const c = {width: w, height: h, getContext: () => ctx,
        toDataURL: () => 'data:image/png;base64,iVBORw0KGgo='};
    ctx.canvas = c;
    return c;
}
const origCreateElement = dom.window.document.createElement.bind(dom.window.document);
dom.window.document.createElement = function (tag, opts) {
    if (String(tag).toLowerCase() === 'canvas') return makeCanvas();
    return origCreateElement(tag, opts);
};
if (typeof global.createImageBitmap === 'undefined') {
    global.createImageBitmap = async () => ({width: 100, height: 100, close: () => {}});
}

const fs = require('fs');
const VirtualMachine = require('scratch-vm');
const Storage = require('scratch-storage');

const vm = new VirtualMachine();
let drawableId = 0;
let skinId = 0;
const bounds = {left: -50, right: -30, top: 10, bottom: -10, width: 20, height: 20};
vm.attachRenderer({
    // каждый спрайт и клон получает свой id — иначе «касается» путает цели
    createDrawable: () => ++drawableId, destroyDrawable: () => {},
    updateDrawableSkinId: () => {}, updateDrawablePosition: () => {},
    updateDrawableDirectionScale: () => {}, updateDrawableVisible: () => {},
    updateDrawableEffect: () => {}, setDrawableOrder: () => {},
    createSkin: () => ++skinId, createSVGSkin: () => ++skinId,
    createBitmapSkin: () => ++skinId,
    destroySkin: () => {}, updateSVGSkin: () => {}, updateBitmapSkin: () => {},
    getSkinSize: () => [100, 100], getSkinRotationCenter: () => [50, 50],
    getCurrentSkinSize: () => [100, 100], getNativeSize: () => [480, 360],
    createTextSkin: () => 1, updateTextSkin: () => {},
    getFencedPositionOfDrawable: (id, pos) => pos,
    getBounds: () => bounds, getBoundsForBubble: () => bounds,
    isTouchingDrawables: () => false, isTouchingColor: () => false,
    extractDrawableScreenSpace: () => ({x: 0, y: 0}),
    drawableTouchingDrawable: () => false,
    draw: () => {}, setLayerGroupOrdering: () => {},
    _nextDrawableId: 1, _allDrawables: [], _allSkins: []
});
vm.attachStorage(new Storage.ScratchStorage());
vm.attachV2BitmapAdapter({
    resize: (canvas, w, h) => makeCanvas(w, h),
    convertDataURIToBinary: () => new Uint8Array(0)
});
vm.attachAudioEngine({
    started: false, on: () => {}, off: () => {},
    audioContext: {currentTime: 0},
    decodeSound: async () => ({sampleRate: 44100, data: new Int16Array(1)}),
    decodeSoundPlayer: async () => {
        const p = {buffer: {}, playbackRate: 1, outputNode: {}, scheduler: {}};
        p.start = () => {}; p.stop = () => {}; p.isPlaying = () => false;
        p.on = () => {}; p.off = () => {}; p.getCurrentTime = () => 0;
        p.context = {currentTime: 0};
        return p;
    },
    createEffectChain: () => ({input: {}, output: {}}),
    playSound: () => {}, stopAllSounds: () => {}, stopSound: () => {},
    createBank: () => ({
        addSoundPlayer: async () => {}, addSound: async () => {},
        playSound: () => {}, stopAllSounds: () => {}, stopSound: () => {},
        getSoundIsPlaying: () => false, setEffects: () => {}, getEffects: () => ({})
    }),
    getPlaybackState: () => ({isPlaying: false})
});

const errors = [];
vm.runtime.on('RUNTIME_ERROR', e => {
    errors.push(e && (e.message || String(e)));
    console.log('RUNTIME_ERROR:', e && (e.message || e));
});

const vars = () => {
    const out = {};
    for (const t of vm.runtime.targets) {
        if (!t.isOriginal) continue;
        for (const id of Object.keys(t.variables)) {
            const v = t.variables[id];
            if (v.type === '') out[v.name] = String(v.value);
        }
    }
    return out;
};
const backdropName = () => {
    const s = vm.runtime.getTargetForStage();
    const c = s.getCostumes()[s.currentCostume];
    return c && c.name;
};
const costumes = () => {
    const out = {};
    for (const t of vm.runtime.targets) {
        if (t.isOriginal && !t.isStage) out[t.sprite.name] = t.getCostumes()[t.currentCostume].name;
    }
    return out;
};
const clones = (name) => vm.runtime.targets.filter(t => !t.isOriginal && (!name || t.sprite.name === name)).length;
const frames = n => new Promise(r => setTimeout(r, n * 16));
const key = (k, down) => vm.postIOData('keyboard', {key: k, isDown: down});


// ---------------------------------------------------------------- столкновения --
// В песочнице нет настоящего рендерера, поэтому «касается» всегда false.
// Для проверки игр с касаниями включаем простую проверку по прямоугольникам:
// размеры костюмов берём прямо из .sb3 (PNG-заголовки), повороты не учитываем.
const JSZip = require('jszip');

function pngSize (buf) {
    if (buf.length < 24 || buf.readUInt32BE(0) !== 0x89504e47) return null;
    return [buf.readUInt32BE(16), buf.readUInt32BE(20)];
}

async function enableSimpleCollisions (file) {
    const zip = await JSZip.loadAsync(fs.readFileSync(file));
    const project = JSON.parse(await zip.file('project.json').async('string'));
    const info = {};                       // 'Спрайт' → {костюм: размеры в пикселях}
    for (const t of project.targets) {
        info[t.name] = {};
        for (const c of t.costumes) {
            const entry = c.md5ext && zip.file(c.md5ext);
            const wh = entry ? pngSize(await entry.async('nodebuffer')) : null;
            if (!wh) continue;
            info[t.name][c.name] = {w: wh[0], h: wh[1],
                cx: c.rotationCenterX, cy: c.rotationCenterY,
                br: c.bitmapResolution || 1};
        }
    }
    const boxOf = (t) => {
        if (!t.visible) return null;        // спрятанные спрайты не сталкиваются
        const c = t.getCostumes()[t.currentCostume];
        const src = (info[t.sprite.name] || {})[c.name];
        if (!src) return null;
        const k = t.size / 100 / src.br;
        const left = t.x - src.cx * k;
        const top = t.y + src.cy * k;
        return {l: left, r: left + src.w * k, t: top, b: top - src.h * k};
    };
    const hit = (a, b) => !!a && !!b && a.l < b.r && b.l < a.r && a.b < b.t && b.b < a.t;
    vm.runtime.renderer.isTouchingDrawables = (drawableID, candidateIDs) => {
        const me = vm.runtime.targets.find(t => t.drawableID === drawableID);
        if (!me) return false;
        const a = boxOf(me);
        return (candidateIDs || []).some((cid) => {
            const other = vm.runtime.targets.find(t => t.drawableID === cid);
            return hit(a, boxOf(other));
        });
    };
}

// Готовит песочницу и отдаёт vm с помощниками. Проект грузим сами:
//   const {vm, frames, key, vars} = boot();
//   await vm.loadProject(fs.readFileSync(file)); vm.runtime.start();
function boot () {
    return {vm, errors, frames, key, vars, backdropName, costumes, clones,
        enableSimpleCollisions};
}

module.exports = {boot, vm, enableSimpleCollisions};
