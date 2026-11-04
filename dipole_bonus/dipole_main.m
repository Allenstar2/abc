%% =====================================================================
%  電偶極的電位與電場：手算理論值 vs MATLAB 數值驗證
%  Electric dipole: hand-calculated theory vs. MATLAB verification
%
%  執行環境: MATLAB R2016b 以上，或 GNU Octave 6 以上
%  執行方式: 把整個資料夾設為 Current Folder，輸入 dipole_main 後按 Enter
%  輸出: results.txt(所有數值結果)、table_points.csv、fig1~fig4 的 PNG 圖
%
%  座標設定(與課本圖相同):
%     +q 放在 (0, 0, +d/2)，-q 放在 (0, 0, -d/2)，偶極矩 p = q*d 指向 +z
%     theta 是與 +z 軸的夾角，phi 是在 x-y 平面上與 +x 軸的夾角
%  =====================================================================
clear; clc; close all;

if exist('results.txt', 'file'), delete('results.txt'); end
diary('results.txt');

%% ---------------- 0. 參數設定 ----------------
k = 8.99e9;          % 1/(4*pi*eps0)，與手算用同一個值，避免常數不同造成誤差
q = 1e-9;            % 電荷量 1 nC
d = 0.01;            % 兩電荷間距 1 cm
p = q*d;             % 偶極矩 [C*m]

zp = +d/2;           % +q 的 z 座標
zm = -d/2;           % -q 的 z 座標

% (1) 精確解: 兩個點電荷的電位直接相加(疊加原理)
V_exact = @(x,y,z) k*q*( 1./sqrt(x.^2 + y.^2 + (z-zp).^2) ...
                       - 1./sqrt(x.^2 + y.^2 + (z-zm).^2) );

% (2) 理論公式(課本的遠場近似，R >> d 時成立): V = p*cos(theta) / (4*pi*eps0*R^2)
V_far = @(R,th) k*p*cos(th)./R.^2;

fprintf('=== Electric dipole: q = %.1e C, d = %.3f m, p = %.1e C*m, k = %.3e ===\n\n', q, d, p, k);

%% ---------------- 1. 三個測試點: V理 vs V電 ----------------
% 刻意挑「近、中、遠」三種距離，觀察遠場公式在哪裡開始不準
%            x      y      z
P = [      0      0     0.02 ;    % P0: 近場，R = 2d，在 z 軸上
        0.03   0.04     0.05 ;    % P1: 中場，R = 7.07d
        0.12   0.16     0.15 ];   % P2: 遠場，R = 25d

nP = size(P,1);
T  = zeros(nP, 11);   % 存表格用

fprintf('--- Part 1: potential at 3 test points ---\n');
fprintf('%-3s %7s %7s %7s | %8s %7s %7s | %11s %11s | %10s %8s\n', ...
    'Pt','x[m]','y[m]','z[m]','R[m]','th[deg]','ph[deg]','V_theory[V]','V_matlab[V]','err[V]','err[%]');
for i = 1:nP
    x = P(i,1); y = P(i,2); z = P(i,3);
    R  = sqrt(x^2 + y^2 + z^2);      % 直角座標 -> 球座標
    th = acos(z/R);
    ph = atan2(y, x);

    Vth = V_far(R, th);              % 理論(手算用的公式)
    Vpc = V_exact(x, y, z);          % 電腦(兩點電荷精確疊加)
    err = abs(Vth - Vpc);
    errp = err/abs(Vpc)*100;

    T(i,:) = [x y z R th*180/pi ph*180/pi Vth Vpc err errp R/d];
    fprintf('P%-2d %7.3f %7.3f %7.3f | %8.5f %7.2f %7.2f | %11.5f %11.5f | %10.3e %8.4f\n', ...
        i-1, x, y, z, R, th*180/pi, ph*180/pi, Vth, Vpc, err, errp);
end
fprintf('\n');

% 存成 CSV，可以直接用 Excel 開，貼到 Word 表格
fid = fopen('table_points.csv', 'w');
fprintf(fid, 'Point,x(m),y(m),z(m),R(m),theta(deg),phi(deg),V_theory(V),V_matlab(V),error(V),error(%%),R/d\n');
for i = 1:nP
    fprintf(fid, 'P%d,%g,%g,%g,%.6f,%.4f,%.4f,%.6f,%.6f,%.6e,%.6f,%.4f\n', i-1, T(i,:));
end
fclose(fid);

%% ---------------- 2. 由 V 求 E: E = -grad(V) ----------------
% 三種算法互相比較:
%   E_num : 對 V_exact 做中央差分(數值微分)，也就是用電腦算 -grad(V)
%   E_coul: 庫侖定律直接把兩個點電荷的電場向量相加(精確解，當作標準答案)
%   E_far : 課本遠場公式 E = kp/R^3 * (2cos(th) R_hat + sin(th) th_hat)
h = 1e-6;   % 差分步長 [m]
fprintf('--- Part 2: E = -grad(V) at the same 3 points ---\n');
fprintf('%-3s | %12s %12s %12s | %12s %12s\n', 'Pt', '|E_num|', '|E_coul|', '|E_far|', ...
        'err_num[%]', 'err_far[%]');
E_tab = zeros(nP, 5);
for i = 1:nP
    x = P(i,1); y = P(i,2); z = P(i,3);

    % (a) 數值梯度(中央差分)
    Ex = -(V_exact(x+h,y,z) - V_exact(x-h,y,z))/(2*h);
    Ey = -(V_exact(x,y+h,z) - V_exact(x,y-h,z))/(2*h);
    Ez = -(V_exact(x,y,z+h) - V_exact(x,y,z-h))/(2*h);
    E_num = [Ex Ey Ez];

    % (b) 庫侖定律精確解
    E_coul = coulombE([x y z], k, q, zp, zm);

    % (c) 遠場公式，球座標分量轉回直角座標
    R  = norm([x y z]); th = acos(z/R); ph = atan2(y,x);
    ER = 2*k*p*cos(th)/R^3;
    Et =   k*p*sin(th)/R^3;
    Rhat  = [sin(th)*cos(ph), sin(th)*sin(ph),  cos(th)];
    thhat = [cos(th)*cos(ph), cos(th)*sin(ph), -sin(th)];
    E_far = ER*Rhat + Et*thhat;

    e_num = norm(E_num - E_coul)/norm(E_coul)*100;   % 向量相對誤差
    e_far = norm(E_far - E_coul)/norm(E_coul)*100;
    E_tab(i,:) = [norm(E_num) norm(E_coul) norm(E_far) e_num e_far];
    fprintf('P%-2d | %12.5f %12.5f %12.5f | %12.3e %12.4f\n', i-1, E_tab(i,:));
end
fprintf('(E in V/m)\n\n');

%% ---------------- 3. 誤差分析: 誤差隨 R/d 的變化 ----------------
% 精確電位做多極展開(Legendre 展開)，只剩奇數項:
%   V_exact = kp*cos(th)/R^2 * [ 1 + (d/R)^2 * P3(cos th)/(4 cos th) + O((d/R)^4) ]
% 所以遠場公式的相對誤差約為 |P3(cos th)/(4 cos th)| * (d/R)^2  ->  log-log 圖斜率 = -2
% 特例: 當 P3(cos th) = 0，也就是 cos^2(th) = 3/5 (th = 39.23 度)，
%       (d/R)^2 項消失，誤差改由 (d/R)^4 項主導 -> 斜率 = -4
P3 = @(c) (5*c.^3 - 3*c)/2;
P5 = @(c) (63*c.^5 - 70*c.^3 + 15*c)/8;

th_magic = acos(sqrt(3/5));                       % 39.23 度
th_list  = [0, 50, 80]*pi/180;
th_list  = [th_list, th_magic];
Rd = logspace(log10(1.5), log10(200), 60);        % R/d 從 1.5 到 200
R  = Rd*d;

fprintf('--- Part 3: far-field error vs R/d (log-log slope fitted for R/d >= 10) ---\n');
fprintf('%10s | %12s | %14s | %s\n', 'theta[deg]', 'fit slope', 'theory slope', 'err% at R/d=10');
figure('Position', [100 100 760 560]); hold on;
mk = {'o','s','^','d'};
cl = [0 0.447 0.741; 0.850 0.325 0.098; 0.466 0.674 0.188; 0.494 0.184 0.556];
leg = {};
for j = 1:numel(th_list)
    th = th_list(j); c = cos(th);
    x = R*sin(th); z = R*cos(th);                 % 在 x-z 平面上(y = 0)
    Ve = V_exact(x, 0*x, z);
    Vf = V_far(R, th);
    errp = abs(Vf - Ve)./abs(Ve)*100;

    % 理論預測的誤差(展開式的第一個非零修正項)
    if abs(P3(c)) > 1e-12
        err_th = abs(P3(c)/(4*c)) * (d./R).^2 * 100;
        slope_th = -2;
    else
        err_th = abs(P5(c)/(16*c)) * (d./R).^4 * 100;
        slope_th = -4;
    end

    sel = Rd >= 10;
    pf  = polyfit(log10(Rd(sel)), log10(errp(sel)), 1);
    e10 = interp1(Rd, errp, 10);
    fprintf('%10.2f | %12.4f | %14d | %.5f\n', th*180/pi, pf(1), slope_th, e10);

    loglog(Rd, errp, mk{j}, 'Color', cl(j,:), 'MarkerSize', 5, 'MarkerFaceColor', cl(j,:));
    loglog(Rd, err_th, '-', 'Color', cl(j,:), 'LineWidth', 1.2);
    leg{end+1} = sprintf('\\theta = %.1f^\\circ  MATLAB', th*180/pi);
    leg{end+1} = sprintf('\\theta = %.1f^\\circ  theory (slope %d)', th*180/pi, slope_th);
end
set(gca, 'XScale', 'log', 'YScale', 'log');
plot([1.5 200], [1 1], 'k--');                    % 1% 參考線
grid on; box on;
xlabel('R / d'); ylabel('Relative error of far-field formula (%)');
title('Far-field dipole formula: error vs. distance');
legend(leg, 'Location', 'southwest', 'FontSize', 8);
xlim([1.5 200]);
print('-dpng', '-r200', 'fig1_error_vs_Rd.png');

% 找出誤差 < 1% 所需的最小 R/d(各角度取最嚴格者)
Rd_fine = logspace(0, 3, 4000);
th_scan = linspace(0, 89, 179)*pi/180;
Rd_need = zeros(size(th_scan));
for j = 1:numel(th_scan)
    th = th_scan(j);
    Ve = V_exact(Rd_fine*d*sin(th), 0*Rd_fine, Rd_fine*d*cos(th));
    Vf = V_far(Rd_fine*d, th);
    e  = abs(Vf - Ve)./abs(Ve)*100;
    idx = find(e >= 1, 1, 'last');
    if isempty(idx), Rd_need(j) = Rd_fine(1); else, Rd_need(j) = Rd_fine(min(idx+1, end)); end
end
[mx, im] = max(Rd_need);
fprintf('Worst case: error < 1%% requires R/d >= %.2f (near theta = %.1f deg)\n', mx, th_scan(im)*180/pi);
fprintf('Near theta = 39.23 deg the (d/R)^2 term vanishes, so the error is much smaller there.\n\n');

% 誤差分布圖(x-z 平面)
L  = 10*d;
gv = linspace(-L, L, 401) + 1e-7;                 % 加一點偏移，避開 z = 0 時 0/0
[X, Z] = meshgrid(gv, gv);
Rg  = sqrt(X.^2 + Z.^2);
Ve  = V_exact(X, 0*X, Z);
Vf  = V_far(Rg, acos(Z./Rg));
Eg  = abs(Vf - Ve)./abs(Ve)*100;
Eg(Rg < 1.5*d) = NaN;                             % 太靠近電荷，不畫
figure('Position', [100 100 640 560]);
contourf(X/d, Z/d, log10(Eg), -3:0.25:2, 'LineStyle', 'none'); hold on;
contour(X/d, Z/d, Eg, [1 1], 'k', 'LineWidth', 2);
contour(X/d, Z/d, Eg, [0.1 0.1], 'w--', 'LineWidth', 1.5);
plot(0, 0.5, 'r+', 'MarkerSize', 10, 'LineWidth', 2);
plot(0, -0.5, 'bo', 'MarkerSize', 7, 'LineWidth', 2);
axis equal tight; cb = colorbar; ylabel(cb, 'log_{10}(error %)');
xlabel('x / d'); ylabel('z / d');
title('Far-field error map (black: 1 %, white dashed: 0.1 %)');
print('-dpng', '-r200', 'fig2_error_map.png');

%% ---------------- 4. 等位線 + 電力線，並驗證 E 垂直於等位線 ----------------
L  = 4*d;
gv = linspace(-L, L, 801);
[X, Z] = meshgrid(gv, gv);
V  = V_exact(X, 0*X, Z);
lv = [20 40 80 160 320 640 1280 2560];
levels = [-fliplr(lv), lv];

figure('Position', [100 100 640 640]); hold on;
contour(X/d, Z/d, V, lv, 'LineColor', [0.80 0.20 0.10], 'LineWidth', 1.0);     % V > 0
contour(X/d, Z/d, V, -lv, 'LineColor', [0.10 0.30 0.80], 'LineWidth', 1.0);    % V < 0
plot([-L L]/d, [0 0], 'Color', [0.4 0.4 0.4], 'LineStyle', ':');            % V = 0 平面

% 電力線: 從 +q 周圍出發，沿 E 的方向用 RK4 一步步積分
r0   = 0.05*d;               % 起點離 +q 的距離
ds   = 0.01*d;               % 每一步的長度
nmax = 6000;
angs = (7.5:15:352.5)*pi/180; % 起始角度(在 x-z 平面)
for a = angs
    r = [r0*sin(a), 0, zp + r0*cos(a)];
    pts = zeros(nmax, 3); pts(1,:) = r; n = 1;
    for s = 1:nmax-1
        f  = @(rr) unitE(rr, k, q, zp, zm);
        k1 = f(r); k2 = f(r + ds/2*k1); k3 = f(r + ds/2*k2); k4 = f(r + ds*k3);
        r  = r + ds/6*(k1 + 2*k2 + 2*k3 + k4);
        n  = n + 1; pts(n,:) = r;
        if norm(r - [0 0 zm]) < r0 || abs(r(1)) > L || abs(r(3)) > L, break; end
    end
    plot(pts(1:n,1)/d, pts(1:n,3)/d, 'k-', 'LineWidth', 0.8);
    m = round(n/2);   % 在電力線中間畫一個小三角形箭頭表示方向
    if m > 2
        u  = pts(m+1,[1 3]) - pts(m-1,[1 3]); u = u/norm(u);   % 前進方向
        nv = [-u(2) u(1)];                                       % 法向量
        c0 = pts(m,[1 3])/d; La = 0.16; Wa = 0.07;              % 箭頭長、半寬(以 d 為單位)
        tri = [c0 + La/2*u; c0 - La/2*u + Wa*nv; c0 - La/2*u - Wa*nv];
        fill(tri(:,1), tri(:,2), 'k', 'EdgeColor', 'k');
    end
end
plot(0,  0.5, 'r+', 'MarkerSize', 12, 'LineWidth', 2.5);
plot(0, -0.5, 'b_', 'MarkerSize', 12, 'LineWidth', 2.5);
text(0.15,  0.75, '+q', 'Color', 'r', 'FontWeight', 'bold');
text(0.15, -0.75, '-q', 'Color', 'b', 'FontWeight', 'bold');
axis equal; xlim([-L L]/d); ylim([-L L]/d); box on;
xlabel('x / d'); ylabel('z / d');
title('Equipotentials (red: V>0, blue: V<0) and E-field lines (black)');
print('-dpng', '-r200', 'fig3_equipotential_fieldlines.png');

% 垂直驗證:
%   用 contourc 取出等位線的折線 -> 每一小段的切線方向 t
%   用庫侖定律算該處的 E(與等位線的計算完全獨立)
%   E 與 t 的夾角應為 90 度
C = contourc(gv, gv, V, levels);
angles = [];
col = 1;
while col < size(C, 2)
    npt = C(2, col);
    xy  = C(:, col+1:col+npt);
    col = col + npt + 1;
    for s = 1:npt-1
        t  = xy(:, s+1) - xy(:, s);
        if norm(t) == 0, continue; end
        mid = (xy(:, s+1) + xy(:, s))/2;
        if norm([mid(1), mid(2)-zp]) < 0.2*d || norm([mid(1), mid(2)-zm]) < 0.2*d, continue; end
        E  = coulombE([mid(1) 0 mid(2)], k, q, zp, zm);
        cosang = abs(t(1)*E(1) + t(2)*E(3)) / (norm(t)*norm([E(1) E(3)]));
        angles(end+1) = acos(min(cosang, 1))*180/pi; %#ok<AGROW>
    end
end
fprintf('--- Part 4: angle between E and equipotential lines ---\n');
fprintf('segments checked : %d\n', numel(angles));
fprintf('mean angle       : %.4f deg\n', mean(angles));
fprintf('min angle        : %.4f deg\n', min(angles));
fprintf('mean |90 - angle|: %.4f deg\n', mean(90 - angles));
fprintf('segments within 1 deg of 90: %.2f %%\n\n', mean(angles > 89)*100);

figure('Position', [100 100 640 420]);
hist(angles, 88.5:0.05:90);
xlim([88.5 90]); grid on;
xlabel('Angle between E and equipotential tangent (deg)'); ylabel('Number of segments');
title(sprintf('E vs. equipotential: %d segments, mean = %.3f deg', numel(angles), mean(angles)));
print('-dpng', '-r200', 'fig4_perpendicular_check.png');

%% ---------------- 5. 驗證 V 與 phi 無關(對 z 軸對稱) ----------------
fprintf('--- Part 5: same R and theta, different phi ---\n');
Rs = 0.05; ths = 45*pi/180;
fprintf('%8s | %12s\n', 'phi[deg]', 'V_matlab[V]');
for phd = [0 37 90 180 270]
    ph = phd*pi/180;
    x = Rs*sin(ths)*cos(ph); y = Rs*sin(ths)*sin(ph); z = Rs*cos(ths);
    fprintf('%8d | %12.8f\n', phd, V_exact(x, y, z));
end
fprintf('\nDone. Figures saved as fig1~fig4 (PNG).\n');
diary off;
