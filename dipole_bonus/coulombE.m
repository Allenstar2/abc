function E = coulombE(r, k, q, zp, zm)
% COULOMBE  電偶極在位置 r = [x y z] 的電場(庫侖定律精確解)
%   +q 在 (0,0,zp)，-q 在 (0,0,zm)
%   E = kq (r - r+)/|r - r+|^3 - kq (r - r-)/|r - r-|^3
    a = r - [0 0 zp];
    b = r - [0 0 zm];
    E = k*q*( a/norm(a)^3 - b/norm(b)^3 );
end
