// Прогон .sb3 в scratch-vm без браузера: ищем ошибки выполнения и смотрим переменные.
//
// Подготовка (один раз):
//   mkdir -p /tmp/sbtest && cd /tmp/sbtest && npm init -y
//   npm install scratch-vm scratch-storage jsdom
//   node /home/user/Star_Wars/tools/vm_test/run.js <файл.sb3> [win|lose]
//
// Скрипт поднимает jsdom (нужен scratch-svg-renderer), подменяет canvas
// и рендерер заглушками, жмёт клавиши и печатает состояние переменных.
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
const bounds = {left: -50, right: -30, top: 10, bottom: -10, width: 20, height: 20};
vm.attachRenderer({
    createDrawable: () => 1, destroyDrawable: () => {},
    updateDrawableSkinId: () => {}, updateDrawablePosition: () => {},
    updateDrawableDirectionScale: () => {}, updateDrawableVisible: () => {},
    updateDrawableEffect: () => {}, setDrawableOrder: () => {},
    createSkin: () => 1, createSVGSkin: () => 1, createBitmapSkin: () => 1,
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
const frames = n => new Promise(r => setTimeout(r, n * 16));
const key = (k, down) => vm.postIOData('keyboard', {key: k, isDown: down});
const brief = () => {
    const v = vars();
    return `этап=${backdropName()} хп_героя=${v['хп_героя']} хп_мола=${v['хп_мола']} игра=${v['игра']} блок=${v['блок']} ранен=${v['ранен']}`;
};

(async () => {
    await vm.loadProject(fs.readFileSync(process.argv[2]));
    console.log('проект загружен, таргетов:', vm.runtime.targets.length);
    vm.runtime.start();
    vm.greenFlag();
    await frames(30);
    console.log('титул:', backdropName(), '|', brief());

    key('ArrowRight', true);
    await frames(6);
    key('ArrowRight', false);
    await frames(4);
    console.log('выбор:', vars()['выбор']);

    key(' ', true);
    await frames(8);
    key(' ', false);
    await frames(20);
    console.log('бой:', backdropName(), '|', brief(), '|', JSON.stringify(costumes()));

    const mode = process.argv[3] || 'win';
    if (mode === 'lose') {
        for (let i = 0; i < 60; i++) {
            await frames(10);
            if (String(vars()['игра']) === '0') break;
        }
        console.log('пассивный бой:', backdropName(), '|', brief());
        await frames(100);
        console.log('экран:', backdropName(), '|', brief());
        await frames(60);
        key(' ', true);
        await frames(25);
        key(' ', false);
        await frames(60);
        console.log('рестарт:', backdropName(), '|', brief());
        console.log('ошибок выполнения:', errors.length, errors.slice(0, 3));
        process.exit(0);
    }

    // активный бой: удары + блок
    let sawHurt = false;
    for (let i = 0; i < 40; i++) {
        key(' ', true);
        await frames(8);
        key(' ', false);
        await frames(4);
        if (String(vars()['ранен']) === '1') sawHurt = true;
        key('ArrowDown', true);
        await frames(22);
        key('ArrowDown', false);
        await frames(6);
        if (String(vars()['игра']) === '0') break;
    }
    console.log('после боя:', backdropName(), '|', brief(), '| ранен видели:', sawHurt);
    await frames(110);
    console.log('финал:', backdropName(), '|', brief(), '|', JSON.stringify(costumes()));
    await frames(60);
    key(' ', true);
    await frames(25);
    key(' ', false);
    await frames(60);
    console.log('после финала:', backdropName(), '|', brief());
    console.log('ошибок выполнения:', errors.length, errors.slice(0, 3));
    process.exit(0);
})().catch(e => {
    console.error('FAIL', e && (e.message || e));
    process.exit(1);
});
