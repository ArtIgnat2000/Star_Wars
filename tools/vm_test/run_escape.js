// Прогон «Побега со „Звезды Смерти“» в scratch-vm: прыжок, удары, финиш.
//
//   node /home/user/Star_Wars/tools/vm_test/run_escape.js <файл.sb3>
//
// Проверяем: Люк прыгает по ПРОБЕЛу и возвращается на пол, препятствия
// выезжают, удар отнимает жизнь, последняя жизнь даёт «Поймали», заезд
// начинается сам, 300 метров дают «Ангар», а ячейка прибавляет жизнь.
const fs = require('fs');
const {boot} = require('./vm_env');
const file = process.argv[2];
const {vm, errors, frames, key, vars, backdropName, clones, enableSimpleCollisions} = boot();

const luke = () => vm.runtime.targets.find(t => t.isOriginal && t.sprite.name === 'Люк');
const brief = () => {
    const v = vars();
    return `этап=${backdropName()} метры=${v['метры']} жизни=${v['жизни']} ` +
           `игра=${v['игра']} прыжок=${v['прыжок']} ` +
           `препятствий=${clones('Препятствие')} ячеек=${clones('Ячейка')} ` +
           `y=${Math.round(luke().y)}`;
};
const setVar = (name, value) => {
    for (const t of vm.runtime.targets) {
        if (!t.isOriginal) continue;
        for (const id of Object.keys(t.variables)) {
            if (t.variables[id].name === name) t.variables[id].value = value;
        }
    }
};

(async () => {
    await vm.loadProject(fs.readFileSync(file));
    console.log('проект загружен, таргетов:', vm.runtime.targets.length);
    await enableSimpleCollisions(file);
    vm.runtime.start();
    vm.greenFlag();
    await frames(20);
    console.log('старт:', brief());
    if (backdropName() !== 'Коридор') throw new Error('фон не «Коридор»');
    if (Number(vars()['жизни']) !== 3) throw new Error('жизни не 3');
    const ground = Math.round(luke().y);            // где стоят ноги Люка
    if (ground < -120 || ground > -60) throw new Error('Люк не на полу');

    // 1. прыжок: взлетает и возвращается на пол
    key(' ', true);
    await frames(3);
    key(' ', false);
    let top = -999;
    for (let i = 0; i < 40; i++) {
        await frames(1);
        top = Math.max(top, luke().y);
        if (Math.round(luke().y) === ground && top > ground + 30) break;
    }
    console.log(`прыжок: вершина y=${Math.round(top)}, приземлился y=${Math.round(luke().y)}`);
    if (top < ground + 35) throw new Error('прыжок слишком низкий');
    if (Math.round(luke().y) !== ground) throw new Error('Люк не приземлился');

    // 2. препятствия выезжают
    for (let i = 0; i < 60 && clones('Препятствие') < 1; i++) await frames(5);
    console.log('препятствия:', brief());
    if (clones('Препятствие') < 1) throw new Error('препятствия не выезжают');
    if (Number(vars()['метры']) < 1) throw new Error('метры не растут');

    // 3. прыжок спасает: перепрыгиваем ящик, жизнь не отнимается
    const livesNow = () => Number(vars()['жизни']);
    const nearest = () => {
        const o = vm.runtime.targets.filter(t => !t.isOriginal && t.sprite.name === 'Препятствие');
        return o.length ? o[0] : null;
    };
    let dodged = false;
    let l0 = livesNow();
    for (let i = 0; i < 300; i++) {
        const o = nearest();
        if (o && o.x - luke().x < 130 && o.x - luke().x > 90 && Math.round(luke().y) === ground) {
            key(' ', true);
            await frames(2);
            key(' ', false);
            for (let j = 0; j < 60; j++) {
                await frames(1);
                if (!nearest() || nearest().x < -280) break;
            }
            dodged = true;
            break;
        }
        await frames(1);
    }
    console.log(`перепрыгнули: ${dodged}, жизни ${l0} → ${livesNow()}`);
    if (!dodged) throw new Error('не дождались препятствия для прыжка');
    if (livesNow() !== l0) throw new Error('прыжок не спас от удара');

    // 4. ячейка появляется и даёт жизнь: прыгаем, когда она подлетает
    const cells = () => vm.runtime.targets.filter(t => !t.isOriginal && t.sprite.name === 'Ячейка');
    let picked = false;
    for (let attempt = 0; attempt < 4 && !picked; attempt++) {
        for (let i = 0; i < 400 && cells().length === 0; i++) await frames(5);
        if (cells().length === 0) throw new Error('ячейки не появляются');
        const before = livesNow();
        for (let i = 0; i < 400; i++) {
            const c = cells()[0];
            if (c && c.x - luke().x < 100 && c.x - luke().x > 60 &&
                Math.round(luke().y) === ground) {
                key(' ', true);
                await frames(2);
                key(' ', false);
                for (let j = 0; j < 40; j++) {
                    await frames(1);
                    if (livesNow() > before) picked = true;
                    if (cells().length === 0 || picked) break;
                }
                break;
            }
            if (cells().length === 0) break;
            await frames(1);
        }
        console.log(`ячейка (попытка ${attempt + 1}): жизни ${before} → ${livesNow()}, поймали=${picked}`);
    }
    if (!picked) throw new Error('ячейка не прибавила жизнь');

    // 5. удар отнимает жизнь, последняя даёт «Поймали»
    // после ячеек игра могла как раз закончиться — дождёмся свежего забега
    for (let i = 0; i < 200 && backdropName() !== 'Коридор'; i++) await frames(5);
    if (backdropName() !== 'Коридор') throw new Error('забег не начался');
    setVar('метры', 0);          // забег начнём с начала, чтобы финиш не мешал
    setVar('жизни', 1);
    for (let i = 0; i < 200 && backdropName() === 'Коридор'; i++) await frames(5);
    console.log('поймали:', brief());
    if (backdropName() !== 'Поймали') throw new Error('нет экрана «Поймали»');

    // 6. забег начинается сам
    for (let i = 0; i < 80 && backdropName() !== 'Коридор'; i++) await frames(10);
    console.log('новый забег:', brief());
    if (backdropName() !== 'Коридор') throw new Error('забег не начался заново');
    if (Number(vars()['жизни']) !== 3) throw new Error('жизни не сброшены');
    if (Number(vars()['метры']) > 20) throw new Error('метры не сброшены');

    // 7. финиш на 300 метрах
    setVar('метры', 299);
    for (let i = 0; i < 40 && backdropName() === 'Коридор'; i++) await frames(10);
    console.log('побег:', brief());
    if (backdropName() !== 'Ангар') throw new Error('нет экрана «Ангар»');

    console.log('ошибок выполнения:', errors.length, errors.slice(0, 3));
    process.exit(errors.length ? 1 : 0);
})().catch(e => {
    console.error('FAIL', e && (e.message || e));
    process.exit(1);
});
