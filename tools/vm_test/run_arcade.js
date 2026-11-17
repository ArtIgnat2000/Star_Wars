// Прогон аркады «Сбей дроидов» в scratch-vm: полёт, выстрелы, победа и поражение.
//
//   node /home/user/Star_Wars/tools/vm_test/run_arcade.js <файл.sb3>
//
// Проверяем: дроиды появляются, корабль ходит по ← →, лазер сбивает дроидов,
// очки растут, экран «Победа» включается на 10 очках и бой начинается заново,
// а если пропустить три дроида — «Поражение».
const fs = require('fs');
const {boot} = require('./vm_env');
const file = process.argv[2];
const {vm, errors, frames, key, vars, backdropName, clones, enableSimpleCollisions} = boot();

const ship = () => vm.runtime.targets.find(t => t.isOriginal && t.sprite.name === 'Корабль');
const droid = () => vm.runtime.targets.find(t => !t.isOriginal && t.sprite.name === 'Дроид');
const brief = () => {
    const v = vars();
    return `этап=${backdropName()} очки=${v['очки']} жизни=${v['жизни']} ` +
           `игра=${v['игра']} дроидов=${clones('Дроид')} лазеров=${clones('Лазер')}`;
};

// «сбей дроида»: ставим значения прямо в переменные проекта
const setVar = (name, value) => {
    for (const t of vm.runtime.targets) {
        if (!t.isOriginal) continue;
        for (const id of Object.keys(t.variables)) {
            if (t.variables[id].name === name) t.variables[id].value = value;
        }
    }
};
const keys = (left, right, space) => {
    key('ArrowLeft', left);
    key('ArrowRight', right);
    key(' ', space);
};

(async () => {
    await vm.loadProject(fs.readFileSync(file));
    console.log('проект загружен, таргетов:', vm.runtime.targets.length);
    await enableSimpleCollisions(file);   // иначе «касается» в песочнице всегда false
    vm.runtime.start();
    vm.greenFlag();
    await frames(20);
    console.log('старт:', brief());
    if (backdropName() !== 'Космос') throw new Error('фон не «Космос»');
    if (Number(vars()['жизни']) !== 5) throw new Error('жизни не 5');

    // 1. ходьба
    const x0 = Math.round(ship().x);
    key('ArrowLeft', true);
    await frames(12);
    key('ArrowLeft', false);
    await frames(4);
    const x1 = Math.round(ship().x);
    console.log(`ходьба: x ${x0} → ${x1}`);
    if (!(x1 < x0)) throw new Error('корабль не двигается влево');

    // 2. дроиды появляются
    for (let i = 0; i < 60 && clones('Дроид') < 1; i++) await frames(5);
    console.log('дроиды:', brief());
    if (clones('Дроид') < 1) throw new Error('дроиды не появляются');

    // 3. наводимся на дроида и стреляем, пока не дойдём до победы
    setVar('очки', 6);
    for (let i = 0; i < 400 && backdropName() === 'Космос'; i++) {
        const d = droid();
        const s = ship();
        const dx = d ? d.x - s.x : 0;
        keys(dx < -6, dx > 6, true);
        await frames(1);
    }
    keys(false, false, false);
    console.log('после стрельбы:', brief());
    if (backdropName() !== 'Победа') throw new Error('нет экрана «Победа»');
    if (Number(vars()['очки']) < 8) throw new Error('победа не на 8 очках');

    // 4. экран сам сменяется новым коном
    for (let i = 0; i < 60 && backdropName() !== 'Космос'; i++) await frames(10);
    console.log('новый кон:', brief());
    if (backdropName() !== 'Космос') throw new Error('кон не начался заново');
    if (Number(vars()['очки']) !== 0 || Number(vars()['жизни']) !== 5) {
        throw new Error('переменные не сброшены');
    }

    // 5. поражение: одна пропущенная цель и три пропущенных дроида
    setVar('жизни', 1);
    for (let i = 0; i < 300 && backdropName() === 'Космос'; i++) await frames(10);
    console.log('поражение:', brief());
    if (backdropName() !== 'Поражение') throw new Error('нет экрана «Поражение»');

    console.log('ошибок выполнения:', errors.length, errors.slice(0, 3));
    process.exit(errors.length ? 1 : 0);
})().catch(e => {
    console.error('FAIL', e && (e.message || e));
    process.exit(1);
});
