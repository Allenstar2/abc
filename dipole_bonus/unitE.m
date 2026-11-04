function u = unitE(r, k, q, zp, zm)
% UNITE  電場方向的單位向量(畫電力線時沿著這個方向走)
    E = coulombE(r, k, q, zp, zm);
    u = E/norm(E);
end
