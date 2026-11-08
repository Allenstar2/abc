const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, WidthType, BorderStyle, ShadingType, PageBreak,
  Footer, PageNumber, LevelFormat, VerticalAlign,
} = require('docx');

// 報告產生腳本：讀取上一層資料夾的 fig*.png，輸出 ../dipole_report.docx
// 用法: node dipole_bonus/tools/build_report.js   (需要 npm 套件 docx)
const DIR = path.join(__dirname, '..');
const OUT = path.join(DIR, 'dipole_report.docx');

const CJK = '標楷體';
const LAT = 'Times New Roman';
const F = { ascii: LAT, hAnsi: LAT, eastAsia: CJK, cs: LAT };
const FM = { ascii: 'Cambria Math', hAnsi: 'Cambria Math', eastAsia: CJK, cs: 'Cambria Math' };
const CONTENT_W = 9026; // A4, 1" margins

// ---------- helpers ----------
const run = (t, o = {}) => new TextRun({ text: t, font: F, size: 24, ...o });
function para(parts, o = {}) {
  const children = (Array.isArray(parts) ? parts : [parts]).map(p => typeof p === 'string' ? run(p) : p);
  return new Paragraph({ children, spacing: { after: 120, line: 360 }, indent: o.noIndent ? undefined : { firstLine: 480 }, alignment: AlignmentType.JUSTIFIED, ...o.p });
}
const b = (t) => run(t, { bold: true });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: F })] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: F })] });
function eq(t, tag) {
  const kids = [new TextRun({ text: t, font: FM, size: 24 })];
  if (tag) kids.push(new TextRun({ text: `\t(${tag})`, font: F, size: 24 }));
  return new Paragraph({
    children: kids, spacing: { before: 60, after: 120 },
    tabStops: tag ? [{ type: 'right', position: CONTENT_W }] : undefined,
    alignment: tag ? AlignmentType.LEFT : AlignmentType.CENTER,
    indent: tag ? { left: 1200 } : undefined,
  });
}
const bullet = (parts) => new Paragraph({
  numbering: { reference: 'bul', level: 0 }, spacing: { after: 80, line: 340 },
  children: (Array.isArray(parts) ? parts : [parts]).map(p => typeof p === 'string' ? run(p) : p),
});
const numbered = (ref, parts) => new Paragraph({
  numbering: { reference: ref, level: 0 }, spacing: { after: 80, line: 340 },
  children: (Array.isArray(parts) ? parts : [parts]).map(p => typeof p === 'string' ? run(p) : p),
});
const caption = (t) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 240 }, children: [run(t, { size: 21, bold: true })] });

function figure(file, w_in, cap) {
  const buf = fs.readFileSync(path.join(DIR, file));
  const W = buf.readUInt32BE(16), H = buf.readUInt32BE(20);
  const wpx = w_in * 96, hpx = Math.round(wpx * H / W);
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120 },
      children: [new ImageRun({ type: 'png', data: buf, transformation: { width: wpx, height: hpx },
        altText: { title: cap, description: cap, name: file } })] }),
    caption(cap),
  ];
}

const border = { style: BorderStyle.SINGLE, size: 4, color: '808080' };
const borders = { top: border, bottom: border, left: border, right: border };
function table(rows, widths, capText) {
  const total = widths.reduce((a, c) => a + c, 0);
  const trs = rows.map((r, i) => new TableRow({
    tableHeader: i === 0, cantSplit: true,
    children: r.map((c, j) => new TableCell({
      borders, width: { size: widths[j], type: WidthType.DXA },
      verticalAlign: VerticalAlign.CENTER,
      shading: i === 0 ? { fill: 'D9E2F3', type: ShadingType.CLEAR, color: 'auto' } : undefined,
      margins: { top: 60, bottom: 60, left: 80, right: 80 },
      children: String(c).split('\n').map(line => new Paragraph({ alignment: AlignmentType.CENTER, keepNext: i < rows.length - 1,
        children: [run(line, { size: 20, bold: i === 0 })] })),
    })),
  }));
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 200, after: 80 }, children: [run(capText, { size: 21, bold: true })] }),
    new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, rows: trs, alignment: AlignmentType.CENTER }),
    new Paragraph({ spacing: { after: 120 }, children: [] }),
  ];
}


const FC = { ascii: 'Consolas', hAnsi: 'Consolas', eastAsia: CJK, cs: 'Consolas' };
function code(cap, src) {
  const lines = src.replace(/^\n/, '').replace(/\n\s*$/, '').split('\n');
  const cell = new TableCell({
    borders, width: { size: CONTENT_W, type: WidthType.DXA },
    shading: { fill: 'F3F3F3', type: ShadingType.CLEAR, color: 'auto' },
    margins: { top: 100, bottom: 100, left: 160, right: 120 },
    children: lines.map(l => new Paragraph({ keepLines: true, keepNext: true, spacing: { after: 0, line: 260 },
      children: [new TextRun({ text: l.length ? l : ' ', font: FC, size: 18 })] })),
  });
  return [
    new Paragraph({ keepNext: true, spacing: { before: 160, after: 60 }, children: [run(cap, { size: 21, bold: true })] }),
    new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W], rows: [new TableRow({ cantSplit: true, children: [cell] })] }),
    new Paragraph({ spacing: { after: 60 }, children: [] }),
  ];
}

// ---------- content ----------
const cover = [
  new Paragraph({ spacing: { before: 2400 }, alignment: AlignmentType.CENTER, children: [run('電磁學 加分作業', { size: 32 })] }),
  new Paragraph({ spacing: { before: 600, after: 200 }, alignment: AlignmentType.CENTER, children: [run('電偶極的電位與電場', { size: 44, bold: true })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [run('手算理論值與 MATLAB 數值驗證', { size: 36, bold: true })] }),
  new Paragraph({ spacing: { before: 2400 }, alignment: AlignmentType.CENTER, children: [run('系級: 電機系 ○ 年級', { size: 28 })] }),
  new Paragraph({ spacing: { before: 200 }, alignment: AlignmentType.CENTER, children: [run('學號: ○○○○○○○○○', { size: 28 })] }),
  new Paragraph({ spacing: { before: 200 }, alignment: AlignmentType.CENTER, children: [run('姓名: ○○○', { size: 28 })] }),
  new Paragraph({ spacing: { before: 200 }, alignment: AlignmentType.CENTER, children: [run('繳交日期: 2026 年 11 月 ○ 日', { size: 28 })] }),
  new Paragraph({ children: [new PageBreak()] }),
];

const body = [
  h1('一、動機與目的'),
  para('課堂上老師展示了電偶極的等位線與電場線圖，並說明 E 場線處處與等位線垂直。課本的電偶極電位公式 V = p cosθ/(4πε₀R²) 是在 R ≫ d 的條件下推導出來的近似式 [1]，但課本沒有說明 R 要多大才算「夠遠」。'),
  para('這份作業依老師的要求選三個點，分別用手算與 MATLAB 計算電位，再比較兩者的誤差。已有研究藉由 MATLAB 輔助電磁學教學 [3]，但這類做法多半著重在把場的圖畫出來。所以我除了驗證計算正確以外，也想藉由 MATLAB 再回答三個問題:'),
  numbered('q', '遠場公式的誤差與距離有什麼關係? 能不能事先用理論預測?'),
  numbered('q', '由 V 經 E = −∇V 求出的電場，是否與庫侖定律直接算出的電場一致?'),
  numbered('q', '能不能用數值的方式，定量證明 E 場線與等位線垂直?'),

  h1('二、理論'),
  h2('2.1 座標設定'),
  para('如圖 3 所示，+q 放在 (0, 0, +d/2)，−q 放在 (0, 0, −d/2)，偶極矩 p = qd 指向 +z 方向。θ 是位置向量與 +z 軸的夾角，φ 是在 x-y 平面上與 +x 軸的夾角，直角座標與球座標的換算為:'),
  eq('R = √(x² + y² + z²)，  θ = cos⁻¹(z/R)，  φ = tan⁻¹(y/x)', '1'),
  h2('2.2 精確解(疊加原理)'),
  para('兩個點電荷的電位直接相加，沒有任何近似，這是本作業中電腦計算 V電 使用的公式:'),
  eq('V = (q/4πε₀)(1/R₊ − 1/R₋)', '2'),
  eq('R₊ = √(x² + y² + (z − d/2)²)，  R₋ = √(x² + y² + (z + d/2)²)', '3'),
  h2('2.3 遠場近似公式(手算 V理 使用)'),
  para('當 R ≫ d 時，1/R₊ − 1/R₋ ≈ d cosθ/R²，代入式 (2) 得到課本的電偶極電位公式 [1]:'),
  eq('V理 = p cosθ / (4πε₀R²)', '4'),
  para('對式 (4) 取 E = −∇V，在球座標下得到:'),
  eq('E = (p / 4πε₀R³)(2cosθ R̂ + sinθ θ̂)', '5'),
  h2('2.4 遠場公式的誤差預測'),
  para('把式 (2) 中的 1/R₊ 與 1/R₋ 用 Legendre 多項式展開 [2]，偶數項會互相抵消，只剩奇數項:'),
  eq('V = (p cosθ / 4πε₀R²) [1 + (d/R)² P₃(cosθ)/(4cosθ) + (d/R)⁴ P₅(cosθ)/(16cosθ) + …]', '6'),
  para('其中 P₃(x) = (5x³ − 3x)/2，P₅(x) = (63x⁵ − 70x³ + 15x)/8。式 (4) 只取了中括號裡的第一項，所以遠場公式的相對誤差大約是:'),
  eq('誤差% ≈ |P₃(cosθ)/(4cosθ)| × (d/R)² × 100%', '7'),
  para('由式 (7) 可以在寫程式之前先做出四個預測:', { noIndent: false }),
  numbered('pred', [b('誤差與 (d/R)² 成正比'), run('，畫成 log-log 圖應該是斜率 −2 的直線。')]),
  numbered('pred', [b('在 z 軸上(θ = 0)可以算出精確值'), run('。此時 V = kqd/(R² − d²/4)，相對誤差剛好是 (d/2R)²，不需要近似。')]),
  numbered('pred', [b('θ ≈ 39.23° 時誤差特別小'), run('。cos²θ = 3/5 時 P₃ = 0，(d/R)² 項消失，誤差改由 (d/R)⁴ 項主導，斜率應該變成 −4。')]),
  numbered('pred', [b('最差的方向在 θ → 90°'), run('。此時係數 |P₃/(4cosθ)| 趨近 3/8，要使誤差 < 1%，需要 R/d > √37.5 ≈ 6.12。')]),

  h1('三、方法'),
  h2('3.1 參數'),
  para('q = 1 nC，d = 1 cm，所以 p = qd = 1×10⁻¹¹ C·m。手算與程式都用 k = 1/(4πε₀) = 8.99×10⁹ N·m²/C²，使常數的取法不會變成誤差的來源，所以 kp = 0.0899 V·m²。'),
  h2('3.2 選點'),
  para('三個點刻意選在近、中、遠三種距離: P0 在 R = 2d、P1 在 R ≈ 7.07d、P2 在 R = 25d，用來觀察遠場公式在哪裡開始不準。座標的選法讓 R 開根號後是整齊的數字，方便手算，P1 與 P2 的 x、y 都不為 0，順便檢查 φ 的換算。'),
  h2('3.3 誤差的定義'),
  eq('誤差 = |V理 − V電|，  誤差% = |V理 − V電| / |V電| × 100%'),
  h2('3.4 MATLAB 程式架構'),
  para('主程式 dipole_main.m 分成五個部分，執行後會自動產生 results.txt(所有數值)、table_points.csv(表 1 的資料)與 fig1~fig4 四張圖:'),
  bullet([b('Part 1: '), run('三個測試點的 V理(式 4)與 V電(式 2)，以及誤差。')]),
  bullet([b('Part 2: '), run('對 V電 做中央差分(步長 h = 10⁻⁶ m)求 −∇V，與庫侖定律及式 (5) 比較。')]),
  bullet([b('Part 3: '), run('R/d 從 1.5 掃到 200，在四個角度畫誤差的 log-log 圖並擬合斜率；再畫 x-z 平面的誤差分布圖。')]),
  bullet([b('Part 4: '), run('畫等位線，電場線用 RK4 從 +q 附近沿 E 的方向一步步積分畫出；再驗證 E 與等位線的夾角。')]),
  bullet([b('Part 5: '), run('固定 R 與 θ、改變 φ，檢查 V 是否與 φ 無關。')]),
  para('各部分的關鍵程式碼與寫法的理由在第四節說明。'),


  h1('四、程式說明'),
  para('這一節節錄 dipole_main.m 中最關鍵的程式碼，說明每一段在做什麼，以及為什麼這樣寫。完整程式只有 dipole_main.m 一個檔案，每一段都有中文註解。'),

  h2('4.1 定義兩條電位公式'),
  ...code('程式 1  參數與兩條電位公式', `
k = 8.99e9;  q = 1e-9;  d = 0.01;  p = q*d;
zp = +d/2;   zm = -d/2;                 % +q、-q 的 z 座標

% 精確解(式 2): 兩個點電荷的電位相加
V_exact = @(x,y,z) k*q*( 1./sqrt(x.^2 + y.^2 + (z-zp).^2) ...
                       - 1./sqrt(x.^2 + y.^2 + (z-zm).^2) );
% 遠場公式(式 4)
V_far = @(R,th) k*p*cos(th)./R.^2;
`),
  para('「@(x,y,z)」是 MATLAB 的匿名函數，定義一次之後就能像數學函數一樣呼叫，例如 V_exact(0, 0, 0.02)。運算符號前面加點(.^、./)代表逐元素運算，使同一個函數可以一次代入整個格點矩陣，後面畫等位線時就不需要再寫兩層迴圈。'),

  h2('4.2 三個測試點的計算'),
  ...code('程式 2  直角座標轉球座標，並計算 V理 與 V電', `
P = [ 0     0     0.02 ;                % P0
      0.03  0.04  0.05 ;                % P1
      0.12  0.16  0.15 ];               % P2
for i = 1:3
    x = P(i,1); y = P(i,2); z = P(i,3);
    R  = sqrt(x^2 + y^2 + z^2);
    th = acos(z/R);                     % θ: 0 ~ 180 度
    ph = atan2(y, x);                   % φ: 會自動判斷象限
    Vth  = V_far(R, th);                % V理
    Vpc  = V_exact(x, y, z);            % V電
    err  = abs(Vth - Vpc);
    errp = err/abs(Vpc)*100;            % 誤差 %
end
`),
  para('矩陣 P 的每一列是一個點，要換點只需要改這裡。φ 用 atan2(y, x) 而不是 atan(y/x)，因為 atan 只會回傳 −90° 到 90°，點在第二、三象限時會算錯，atan2 會依 x 與 y 的正負判斷象限。θ 用 acos，範圍 0° 到 180° 剛好符合球座標的定義。'),

  h2('4.3 用數值微分求 E = −∇V'),
  ...code('程式 3  中央差分求梯度，並與庫侖定律比較', `
h = 1e-6;                               % 差分步長 [m]
Ex = -(V_exact(x+h,y,z) - V_exact(x-h,y,z))/(2*h);
Ey = -(V_exact(x,y+h,z) - V_exact(x,y-h,z))/(2*h);
Ez = -(V_exact(x,y,z+h) - V_exact(x,y,z-h))/(2*h);
E_num  = [Ex Ey Ez];
E_coul = coulombE([x y z], k, q, zp, zm);         % 庫侖定律(標準答案)
e_num  = norm(E_num - E_coul)/norm(E_coul)*100;   % 向量相對誤差
`),
  para('偏微分 ∂V/∂x 的定義是 x 變化一點點時 V 的變化率，所以在 x 的前後各移 h，用兩點連線的斜率來近似，這叫中央差分。它的誤差與 h² 成正比，比只往一邊移的前向差分(誤差與 h 成正比)準確。h 不能太大也不能太小: 太大時近似不準，太小時兩個非常接近的 V 相減，浮點數的捨入誤差會被放大。h = 10⁻⁶ m 約為 d 的萬分之一，表 3 的誤差在 10⁻⁷ % 等級，表示這個 h 取得合適。'),
  ...code('程式 4  區域函數 coulombE: 用庫侖定律算電場(寫在 dipole_main.m 最後面)', `
function E = coulombE(r, k, q, zp, zm)
    a = r - [0 0 zp];                   % 從 +q 指向 r 的向量
    b = r - [0 0 zm];                   % 從 -q 指向 r 的向量
    E = k*q*( a/norm(a)^3 - b/norm(b)^3 );
end
`),
  para('a/|a|³ 就是 â/|a|²，也就是庫侖定律中「方向為單位向量、大小與距離平方成反比」的寫法。+q 與 −q 的電場向量相減即為總電場。'),
  para('庫侖定律的電場在程式 3、程式 6(畫電場線)與程式 7(垂直驗證)共用到三次，所以寫成函數重複使用。它需要好幾行計算，不能像 V_exact 一樣寫成一行的匿名函數，所以用 function 定義，放在 dipole_main.m 的最後面。這種寫法叫區域函數(local function)，MATLAB R2016b 以後支援，好處是整個作業只有一個程式檔，不會因為少複製一個檔案而無法執行。另一個區域函數 unitE 只是把 coulombE 的結果除以大小，得到電場的方向。'),

  h2('4.4 誤差掃描與擬合斜率'),
  ...code('程式 5  固定 θ，讓 R/d 從 1.5 掃到 200，再擬合 log-log 斜率', `
Rd = logspace(log10(1.5), log10(200), 60);       % R/d 取 60 個點
R  = Rd*d;
x  = R*sin(th);  z = R*cos(th);                   % 沿著固定 θ 的射線往外
Ve = V_exact(x, 0*x, z);
Vf = V_far(R, th);
errp = abs(Vf - Ve)./abs(Ve)*100;
sel = Rd >= 10;
pf  = polyfit(log10(Rd(sel)), log10(errp(sel)), 1);   % pf(1) 就是斜率
`),
  para('logspace 在對數尺度上等距取點，使 log-log 圖上的點分布均勻。若誤差 = C·(d/R)ⁿ，兩邊取對數後 log(誤差) = log C − n·log(R/d)，在 log-log 圖上是一條直線，所以用 polyfit 擬合一次多項式，pf(1) 就是斜率 −n。只取 R/d ≥ 10 的點是因為近處高階項還有影響，曲線還不是純直線。'),

  h2('4.5 用 RK4 畫電場線'),
  ...code('程式 6  從 +q 旁邊出發，沿 E 的方向一步步積分(節錄)', `
f = @(rr) unitE(rr, k, q, zp, zm);      % E 方向的單位向量
r = [r0*sin(a), 0, zp + r0*cos(a)];     % 起點: +q 旁邊，角度 a
for s = 1:nmax-1
    k1 = f(r);
    k2 = f(r + ds/2*k1);
    k3 = f(r + ds/2*k2);
    k4 = f(r + ds*k3);
    r  = r + ds/6*(k1 + 2*k2 + 2*k3 + k4);
    if norm(r - [0 0 zm]) < r0 || abs(r(1)) > L || abs(r(3)) > L
        break;                          % 到達 -q 或超出畫圖範圍
    end
end
`),
  para('電場線的定義是線上每一點的切線方向都是 E，所以從 +q 旁邊出發，每次沿 E 的方向走一小步 ds，把走過的點連起來就是電場線。這裡用 E 的單位向量而不是 E 本身，使每一步的長度固定，靠近電荷(E 很大)時才不會一步跳太遠。RK4(四階 Runge-Kutta)在一步之內取四個位置的方向做加權平均，比只用起點方向的 Euler 法準確，曲線不會越走越偏。起點角度每 15° 取一條，共 24 條。'),

  h2('4.6 驗證 E 垂直於等位線'),
  ...code('程式 7  取出等位線的切線，計算與 E 的夾角(節錄)', `
C = contourc(gv, gv, V, levels);        % 等位線的座標資料
col = 1;
while col < size(C, 2)
    npt = C(2, col);                    % 這一段等位線有幾個點
    xy  = C(:, col+1:col+npt);          % 這一段的 (x, z) 座標
    col = col + npt + 1;
    for s = 1:npt-1
        t   = xy(:, s+1) - xy(:, s);    % 切線方向
        mid = (xy(:, s+1) + xy(:, s))/2;
        E   = coulombE([mid(1) 0 mid(2)], k, q, zp, zm);
        cosang = abs(t(1)*E(1) + t(2)*E(3)) / (norm(t)*norm([E(1) E(3)]));
        angles(end+1) = acos(min(cosang, 1))*180/pi;
    end
end
`),
  para('contourc 的輸出是一個 2 列的矩陣，每一段等位線前面有一欄 [等位值; 點數]，後面接著該段各點的 x、z 座標，所以用 while 迴圈一段一段讀出來。相鄰兩點相減就是切線向量 t，再用內積 cos = t·E/(|t||E|) 求夾角。E 是用庫侖定律算的，與 V 的格點及 contourc 無關，所以這是兩種獨立方法的互相驗證。如果改用 −∇V 算 E，結果一定是 90°，就沒有驗證的意義。實際程式還會略過太靠近電荷的線段，因為那裡等位線曲率太大，格點不夠密。'),

  h1('五、結果'),
  h2('5.1 三個測試點: V理 與 V電 的比較'),
  ...table([
    ['點', '(x, y, z)\n[m]', '(R [m], θ, φ)', 'V理 [V]\n(手算)', 'V電 [V]\n(MATLAB)', '誤差 [V]', '誤差 %'],
    ['P0', '(0, 0, 0.02)', '(0.02, 0°, —)', '224.75', '239.733', '14.98', '6.2500 %'],
    ['P1', '(0.03, 0.04, 0.05)', '(0.07071, 45°, 53.13°)', '12.7138', '12.6977', '1.606×10⁻²', '0.1265 %'],
    ['P2', '(0.12, 0.16, 0.15)', '(0.25, 53.13°, 53.13°)', '0.86304', '0.86283', '2.072×10⁻⁴', '0.0240 %'],
  ], [700, 1700, 1900, 1150, 1250, 1176, 1150], '表 1  三個測試點的電位比較(P0 在 z 軸上，φ 沒有定義也不影響結果)'),

  h2('5.2 手算過程'),
  para([b('P0 (0, 0, 0.02): '), run('R = 0.02 m，cosθ = 1。V理 = 0.0899 × 1 / (0.02)² = 0.0899 / (4×10⁻⁴) = 224.75 V。P0 在 z 軸上，精確值也能手算: V電 = 8.99 × (1/0.015 − 1/0.025) = 8.99 × 26.667 = 239.73 V，相對誤差 (d/2R)² = (0.25)² = 6.25%，與 MATLAB 完全相同。')], { noIndent: true }),
  para([b('P1 (0.03, 0.04, 0.05): '), run('R = √(0.0009 + 0.0016 + 0.0025) = √0.005 = 0.07071 m，cosθ = 0.05/0.07071 = 0.7071，θ = 45°，φ = tan⁻¹(0.04/0.03) = 53.13°。V理 = 0.0899 × 0.7071 / 0.005 = 12.714 V。')], { noIndent: true }),
  para([b('P2 (0.12, 0.16, 0.15): '), run('R = √(0.0144 + 0.0256 + 0.0225) = √0.0625 = 0.25 m，cosθ = 0.15/0.25 = 0.6，θ = 53.13°，φ = tan⁻¹(0.16/0.12) = 53.13°。V理 = 0.0899 × 0.6 / 0.0625 = 0.86304 V。')], { noIndent: true }),
  para('再用式 (7) 預測三個點的誤差，與 MATLAB 的結果比較如表 2。P0 與 P2 幾乎完全一樣，P1 有約 1% 的差距，推測是式 (7) 只取到第一個修正項，P1 距離較近，(d/R)⁴ 項的影響還看得出來。'),
  ...table([
    ['點', 'R/d', '(d/R)²', '|P₃/(4cosθ)|', '式 (7) 預測誤差 %', 'MATLAB 誤差 %'],
    ['P0', '2', '0.25', '0.25', '6.25 (精確值)', '6.2500'],
    ['P1', '7.07', '0.02', '0.0625', '0.125', '0.1265'],
    ['P2', '25', '0.0016', '0.15', '0.0240', '0.0240'],
  ], [900, 1100, 1300, 1700, 2100, 1926], '表 2  以式 (7) 預測的誤差與 MATLAB 結果比較'),

  h2('5.3 由 V 求 E: E = −∇V'),
  para('表 3 中 |E_num| 是對 V電 做數值微分得到的電場，|E_coul| 是用庫侖定律把兩個點電荷的電場向量直接相加，|E_far| 是式 (5) 的遠場公式。誤差都以 E_coul 為標準，用向量差的大小計算。'),
  ...table([
    ['點', '|E_num| [V/m]\n(−∇V 數值)', '|E_coul| [V/m]\n(庫侖定律)', '|E_far| [V/m]\n(式 5)', 'E_num 誤差 %', 'E_far 誤差 %'],
    ['P0', '25571.556', '25571.556', '22475.000', '6.0×10⁻⁷', '12.11'],
    ['P1', '402.136', '402.136', '402.045', '2.7×10⁻⁸', '0.550'],
    ['P2', '8.29643', '8.29643', '8.29796', '6.9×10⁻⁸', '0.048'],
  ], [700, 1700, 1700, 1600, 1600, 1726], '表 3  三種方法算出的電場大小比較'),

  h2('5.4 誤差隨距離的變化'),
  ...figure('fig1_error_vs_Rd.png', 5.6, '圖 1  遠場公式的相對誤差與 R/d 的關係(點: MATLAB，線: 式 (6) 的理論預測)'),
  ...table([
    ['θ', '擬合斜率 (R/d ≥ 10)', '理論斜率', 'R/d = 10 時的誤差 %'],
    ['0°', '−2.0000', '−2', '0.2506'],
    ['50°', '−2.0008', '−2', '0.1174'],
    ['80°', '−2.0002', '−2', '0.3573'],
    ['39.23°', '−3.9999', '−4', '0.00034'],
  ], [1600, 2600, 1800, 3026], '表 4  log-log 圖的擬合斜率'),
  ...figure('fig2_error_map.png', 5.0, '圖 2  x-z 平面上遠場公式的誤差分布(黑線: 1%，白虛線: 0.1%)'),
  para('依掃描結果，在所有方向上要使誤差 < 1%，最嚴格的條件是 R/d ≥ 6.13(出現在 θ ≈ 88.5°)，與式 (7) 預測的 6.12 相符。z 軸方向只要 R/d ≥ 5 就夠了。'),

  h2('5.5 等位線、電場線與垂直驗證'),
  ...figure('fig3_equipotential_fieldlines.png', 4.8, '圖 3  電偶極的等位線(紅: V > 0，藍: V < 0)與電場線(黑)'),
  para('驗證垂直的方法是: 用 MATLAB 的 contourc 把等位線取成許多小線段，算出每一段的切線方向 t，再用庫侖定律算該處的 E，求 t 與 E 的夾角。等位線來自格點上的 V，E 來自庫侖定律，兩者的計算過程互相獨立。'),
  ...figure('fig4_perpendicular_check.png', 5.2, '圖 4  E 與等位線切線夾角的分布'),
  para('共檢查 14252 段，平均夾角 89.892°，最小 88.59°，有 99.78% 的線段與 90° 相差不到 1°。'),

  h2('5.6 V 與 φ 無關'),
  ...table([
    ['φ', '0°', '37°', '90°', '180°', '270°'],
    ['V電 [V]', '25.36264478', '25.36264478', '25.36264478', '25.36264478', '25.36264478'],
  ], [1226, 1560, 1560, 1560, 1560, 1560], '表 5  R = 0.05 m、θ = 45° 時，不同 φ 的電位'),

  h1('六、討論'),
  para([b('對 V理 與 V電 差異來源的分析: '), run('兩者用同一個 k 值，雙精度浮點數的捨入誤差約 10⁻¹⁶，所以表 1 的誤差不是電腦算錯，而是遠場公式本身忽略了高階項。表 2 中式 (7) 的預測與 MATLAB 幾乎一致，可以證明這個推論。')], { noIndent: true }),
  para([b('對誤差與距離關係的分析: '), run('圖 1 中三個一般角度的擬合斜率都是 −2.000，與式 (7) 的預測相符。實際上的意義是: 距離變成 10 倍，誤差會變成 1/100。以 1% 為標準，R ≥ 6.13d 時遠場公式在任何方向都可以放心使用，P0(R = 2d)誤差達 6.25%，就不適合用遠場公式。')], { noIndent: true }),
  para([b('對 θ ≈ 39.23° 的分析: '), run('這個角度的誤差比其他角度小了約三個數量級，斜率也從 −2 變成 −4，與第二節預測的一樣。圖 2 中從原點往外延伸的深色斜線就是這個角度。推測原因是 P₃(cosθ) = 0，使第一個修正項剛好消失。')], { noIndent: true }),
  para([b('對 E 場的分析: '), run('數值微分的 E_num 與庫侖定律的 E_coul 相差不到 10⁻⁶ %，證明 E = −∇V 在數值上成立。遠場公式的 E 在 P0 誤差是 12.11%，大約是電位誤差的兩倍。在 z 軸上可以算出精確解 E = 2kqdR/(R² − d²/4)²，誤差為 1 − (1 − (d/2R)²)² = 12.11%，與 MATLAB 一致。推測原因是 E 比 V 多了一次對 R 的微分，高階項的相對比例變大。')], { noIndent: true }),
  para([b('對垂直驗證的分析: '), run('平均夾角 89.892°，與 90° 相差約 0.1°。這個差距可能來自 contourc 用格點做線性內插，等位線被近似成許多短直線，在曲率大的地方(靠近電荷)切線方向會有些偏差。若把格點加密，偏差應該會再變小。')], { noIndent: true }),
  para([b('對 φ 的分析: '), run('表 5 中五個 φ 的電位完全相同，說明電偶極的場對 z 軸對稱，所以只在 x-z 平面畫圖就能代表整個空間。')], { noIndent: true }),

  h1('七、結論'),
  para('手算的遠場公式與 MATLAB 的精確解在遠處非常接近，P2(R = 25d)誤差只有 0.024%，但在近處 P0(R = 2d)誤差達 6.25%。誤差與 (d/R)² 成正比，可以事先用 Legendre 展開準確預測，在 θ ≈ 39.23° 時誤差更是降到與 (d/R)⁴ 成正比。由 V 求出的 E 與庫侖定律一致，E 與等位線的夾角也在數值上驗證為 90°。'),
  para('這份作業的限制是只考慮理想的點電荷，等位線的垂直驗證也受格點解析度影響。之後可以把同樣的方法用在電四極或有限長度的線電荷上，觀察誤差的斜率是否也能由多極展開預測。'),

  h1('參考文獻'),
  para('[1] D. K. Cheng, Field and Wave Electromagnetics, 2nd ed. Reading, MA, USA: Addison-Wesley, 1989.', { noIndent: true }),
  para('[2] D. J. Griffiths, Introduction to Electrodynamics, 4th ed. Cambridge, U.K.: Cambridge Univ. Press, 2017.', { noIndent: true }),
  para('[3] M. de Magistris, “A MATLAB-based virtual laboratory for teaching introductory quasi-stationary electromagnetics,” IEEE Trans. Educ., vol. 48, no. 1, pp. 81–88, 2005, doi: 10.1109/TE.2004.832872.', { noIndent: true }),

  h1('附錄: 檔案說明與執行方式'),
  ...table([
    ['檔案', '說明'],
    ['dipole_main.m', '唯一的程式檔，最後面含 coulombE、unitE 兩個區域函數，\n執行後產生下列所有結果'],
    ['results.txt', 'Part 1~5 所有數值結果'],
    ['table_points.csv', '表 1 的資料，可用 Excel 開啟'],
    ['fig1~fig4 (.png)', '報告中的圖 1~圖 4'],
  ], [2600, 6426], '表 6  壓縮檔內容'),
  para('執行方式: 解壓縮後在 MATLAB 把 Current Folder 設為該資料夾，在 Command Window 輸入 dipole_main 後按 Enter(或在 Editor 開啟 dipole_main.m 後按 Run)，約十幾秒可完成。程式只用到 MATLAB 的基本函數，不需要額外的 Toolbox，需要 MATLAB R2016b 以上的版本。'),
];

const doc = new Document({
  creator: 'student',
  title: '電偶極的電位與電場: 手算理論值與 MATLAB 數值驗證',
  styles: {
    default: { document: { run: { font: F, size: 24 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: F, size: 32, bold: true, color: '000000' },
        paragraph: { spacing: { before: 360, after: 160 }, keepNext: true, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: F, size: 26, bold: true, color: '000000' },
        paragraph: { spacing: { before: 240, after: 100 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: 'q', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '(%1)', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 960, hanging: 480 } } } }] },
      { reference: 'pred', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '(%1)', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 960, hanging: 480 } } } }] },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } }, titlePage: true },
    footers: {
      default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ children: [PageNumber.CURRENT], font: F, size: 20 })] })] }),
      first: new Footer({ children: [new Paragraph({ children: [] })] }),
    },
    children: [...cover, ...body],
  }],
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log('wrote', OUT); });
