// Прогон «Гонок на подах» в scratch-vm: полёт, скалы, финиш и авария.
//
//   node /home/user/Star_Wars/tools/vm_test/run_podrace.js <файл.sb3>
//
// Проверяем: под слушается ↑ ↓ и не улетает с трассы, скалы появляются,
// столкновение отнимает жизнь, 400 метров дают «Финиш», а после
// последней аварии — экран «Авария»; затем заезд начинается сам.
const fs = require('fs');
const {boot} = require('./vm_env');
const file = process.argv[2];
const {vm, errors, frames, key, vars, backdropName, clones, enableSimpleCollisions} = boot();

const pod = () => vm.runtime.targets.find(t => t.isOriginal && t.sprite.name === 'Под');
const brief = () => {
    const v = vars();
    return `этап=${backdropName()} метры=${v['метры']} жизни=${v['жизни']} ` +
           `игра=${v['игра']} скал=${clones('Скала')} y=${Math.round(pod().y)}`;
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
    if (backdropName() !== 'Трасса') throw new Error('фон не «Трасса»');
    if (Number(vars()['жизни']) !== 4) throw new Error('жизни не 4');

    // 1. под слушается стрелок
    const y0 = Math.round(pod().y);
    key('ArrowUp', true);
    await frames(10);
    key('ArrowUp', false);
    await frames(3);
    const y1 = Math.round(pod().y);
    key('ArrowDown', true);
    await frames(20);
    key('ArrowDown', false);
    await frames(3);
    const y2 = Math.round(pod().y);
    console.log(`полёт: y ${y0} → ${y1} → ${y2}`);
    if (!(y1 > y0)) throw new Error('↑ не поднимает под');
    if (!(y2 < y1)) throw new Error('↓ не опускает под');

    // 2. под не улетает с трассы
    key('ArrowDown', true);
    await frames(40);
    key('ArrowDown', false);
    await frames(3);
    console.log('упёрлись вниз:', brief());
    if (pod().y < -111) throw new Error('под улетел за нижний край');

    // 3. скалы появляются
    for (let i = 0; i < 60 && clones('Скала') < 1; i++) await frames(5);
    console.log('скалы:', brief());
    if (clones('Скала') < 1) throw new Error('скалы не появляются');
    if (Number(vars()['метры']) < 1) throw new Error('метры не растут');

    // 4. авария: одна жизнь и никакого уклонения
    setVar('жизни', 1);
    for (let i = 0; i < 300 && backdropName() === 'Трасса'; i++) await frames(10);
    console.log('авария:', brief());
    if (backdropName() !== 'Авария') throw new Error('нет экрана «Авария»');

    // 5. заезд начинается сам
    for (let i = 0; i < 60 && backdropName() !== 'Трасса'; i++) await frames(10);
    console.log('новый заезд:', brief());
    if (backdropName() !== 'Трасса') throw new Error('заезд не начался заново');
    if (Number(vars()['метры']) > 20 || Number(vars()['жизни']) !== 4) {
        throw new Error('переменные не сброшены');
    }

    // 6. финиш на 400 метрах
    setVar('метры', 399);
    for (let i = 0; i < 40 && backdropName() === 'Трасса'; i++) await frames(10);
    console.log('финиш:', brief());
    if (backdropName() !== 'Финиш') throw new Error('нет экрана «Финиш»');

    console.log('ошибок выполнения:', errors.length, errors.slice(0, 3));
    process.exit(errors.length ? 1 : 0);
})().catch(e => {
    console.error('FAIL', e && (e.message || e));
    process.exit(1);
});
