// Прогон .sb3 в scratch-vm без браузера: ищем ошибки выполнения и смотрим переменные.
//
// Подготовка (один раз):
//   mkdir -p /tmp/sbtest && cd /tmp/sbtest && npm init -y
//   npm install scratch-vm scratch-storage jsdom
//   node /home/user/Star_Wars/tools/vm_test/run.js <файл.sb3> [win|lose]
//
// Скрипт поднимает jsdom (нужен scratch-svg-renderer), подменяет canvas
// и рендерер заглушками, жмёт клавиши и печатает состояние переменных.
// Вся «песочница» — в vm_env.js, ей же пользуется run_arcade.js.
const fs = require('fs');
const {boot} = require('./vm_env');
const file = process.argv[2];
const {vm, errors, frames, key, vars, backdropName, costumes} = boot();

const brief = () => {
    const v = vars();
    return `этап=${backdropName()} хп_героя=${v['хп_героя']} хп_мола=${v['хп_мола']} игра=${v['игра']} блок=${v['блок']} ранен=${v['ранен']}`;
};

(async () => {
    await vm.loadProject(fs.readFileSync(file));
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
