// Прогон «Дагобы: тренировка Силы» в scratch-vm: кольцо за мышью, камни, финал.
//
//   node /home/user/Star_Wars/tools/vm_test/run_force.js <файл.sb3>
//
// Проверяем: кольцо «Сила» летит за курсором, камень можно поймать (счёт растёт),
// утонувший камень отнимает жизнь, «свет Силы» прибавляет жизнь, 10 камней дают
// «Победа», последняя жизнь — «Провал», затем игра начинается заново.
const fs = require('fs');
const {boot} = require('./vm_env');
const file = process.argv[2];
const {vm, errors, frames, vars, backdropName, clones, enableSimpleCollisions} = boot();

const ring = () => vm.runtime.targets.find(t => t.isOriginal && t.sprite.name === 'Сила');
const brief = () => {
    const v = vars();
    return `этап=${backdropName()} камни=${v['камни']} жизни=${v['жизни']} ` +
           `игра=${v['игра']} падение=${v['падение']} пауза=${v['пауза']} ` +
           `камней=${clones('Камень')} свет=${clones('Свет')} ` +
           `кольцо=(${Math.round(ring().x)},${Math.round(ring().y)})`;
};
const setVar = (name, value) => {
    for (const t of vm.runtime.targets) {
        if (!t.isOriginal) continue;
        for (const id of Object.keys(t.variables)) {
            if (t.variables[id].name === name) t.variables[id].value = value;
        }
    }
};
// сцена 480×360: переводим координаты Scratch в координаты «мыши»
const mouse = (sx, sy) => vm.postIOData('mouse', {
    x: sx + 240, y: 180 - sy, canvasWidth: 480, canvasHeight: 360});
const away = () => mouse(235, 175);        // курсор в углу — ничего не ловим

(async () => {
    await vm.loadProject(fs.readFileSync(file));
    console.log('проект загружен, таргетов:', vm.runtime.targets.length);
    await enableSimpleCollisions(file);
    vm.runtime.start();
    vm.greenFlag();
    away();
    await frames(20);
    console.log('старт:', brief());
    if (backdropName() !== 'Болото') throw new Error('фон не «Болото»');
    if (Number(vars()['жизни']) !== 3) throw new Error('жизни не 3');

    // 1. кольцо летит за курсором
    mouse(-120, 40);
    await frames(5);
    const p1 = [Math.round(ring().x), Math.round(ring().y)];
    mouse(100, -60);
    await frames(5);
    const p2 = [Math.round(ring().x), Math.round(ring().y)];
    console.log('кольцо:', p1, '→', p2);
    if (Math.abs(p1[0] + 120) > 3 || Math.abs(p1[1] - 40) > 3) throw new Error('кольцо не за курсором');
    if (Math.abs(p2[0] - 100) > 3 || Math.abs(p2[1] + 60) > 3) throw new Error('кольцо не за курсором');

    // 2. камень появляется и его можно поймать
    const rocks = () => vm.runtime.targets.filter(t => !t.isOriginal && t.sprite.name === 'Камень');
    for (let i = 0; i < 200 && rocks().length === 0; i++) await frames(5);
    console.log('камень:', brief());
    if (rocks().length === 0) throw new Error('камни не падают');
    const before = Number(vars()['камни']);
    let caught = false;
    for (let i = 0; i < 400; i++) {
        const r = rocks()[0];
        if (r) mouse(r.x, r.y);
        await frames(1);
        if (Number(vars()['камни']) > before) { caught = true; break; }
    }
    console.log(`поймали камень: ${before} → ${vars()['камни']}, темп ${vars()['падение']}`);
    if (!caught) throw new Error('камень не поймался');
    if (Number(vars()['падение']) >= -3) throw new Error('темп не вырос');

    // 3. если курсор увести — камень тонет и жизнь убывает
    away();
    const lives = Number(vars()['жизни']);
    let sank = false;
    for (let i = 0; i < 300; i++) {
        await frames(5);
        if (Number(vars()['жизни']) < lives) { sank = true; break; }
    }
    console.log(`утонул камень: жизни ${lives} → ${vars()['жизни']}`);
    if (!sank) throw new Error('утонувший камень не отнял жизнь');

    // 4. «свет Силы» прибавляет жизнь
    const orbs = () => vm.runtime.targets.filter(t => !t.isOriginal && t.sprite.name === 'Свет');
    const lives2 = Number(vars()['жизни']);
    let bonus = false;
    for (let i = 0; i < 600 && !bonus; i++) {
        const o = orbs()[0];
        if (o) mouse(o.x, o.y); else away();
        await frames(1);
        if (Number(vars()['жизни']) > lives2) bonus = true;
    }
    console.log(`свет Силы: жизни ${lives2} → ${vars()['жизни']}, бонус=${bonus}`);
    if (!bonus) throw new Error('свет Силы не дал жизнь');

    // 5. десятый камень — победа
    setVar('камни', 9);
    for (let i = 0; i < 500 && backdropName() === 'Болото'; i++) {
        const r = rocks()[0];
        if (r) mouse(r.x, r.y); else away();
        await frames(1);
    }
    console.log('победа:', brief());
    if (backdropName() !== 'Победа') throw new Error('нет экрана «Победа»');

    // 6. новый забег начинается сам
    for (let i = 0; i < 80 && backdropName() !== 'Болото'; i++) await frames(10);
    console.log('новый забег:', brief());
    if (backdropName() !== 'Болото') throw new Error('игра не началась заново');
    if (Number(vars()['камни']) !== 0 || Number(vars()['жизни']) !== 3) {
        throw new Error('переменные не сброшены');
    }

    // 7. последняя жизнь — «Провал»
    away();
    setVar('жизни', 1);
    for (let i = 0; i < 300 && backdropName() === 'Болото'; i++) await frames(5);
    console.log('провал:', brief());
    if (backdropName() !== 'Провал') throw new Error('нет экрана «Провал»');

    console.log('ошибок выполнения:', errors.length, errors.slice(0, 3));
    process.exit(errors.length ? 1 : 0);
})().catch(e => {
    console.error('FAIL', e && (e.message || e));
    process.exit(1);
});
