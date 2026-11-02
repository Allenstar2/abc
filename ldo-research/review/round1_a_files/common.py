"""共用工具：產生 netlist、呼叫 ngspice、讀 wrdata 輸出。"""
import os, subprocess, numpy as np

SCR = os.path.dirname(os.path.abspath(__file__))
MODEL = "/home/user/abc/ldo-research/sim/models/180nm_bulk.pm"
RES = os.path.join(SCR, "res")
FIG = os.path.join(SCR, "figs")
NET = os.path.join(SCR, "net")
for d in (RES, FIG, NET):
    os.makedirs(d, exist_ok=True)


def run(netlist_text, name, keep=True, timeout=600):
    """把 netlist 寫到 sim/netlists/<name>.cir 並以 batch 模式執行。回傳 stdout。"""
    path = os.path.join(NET, name + ".cir")
    with open(path, "w") as f:
        f.write(netlist_text)
    p = subprocess.run(["ngspice", "-b", path], cwd=NET, capture_output=True,
                       text=True, timeout=timeout)
    out = p.stdout + p.stderr
    with open(os.path.join(RES, name + ".log"), "w") as f:
        f.write("\n".join(l for l in out.splitlines() if "unrecognized parameter" not in l))
    if p.returncode != 0 or "fatal" in out.lower():
        print(f"[warn] ngspice returncode={p.returncode} for {name}")
    return out


def load_wrdata(path):
    """wrdata 格式：每個向量一對 (x, y) 欄位。回傳 x 與 y 陣列列表。"""
    a = np.loadtxt(path, ndmin=2)
    x = a[:, 0]
    ys = [a[:, 2 * i + 1] for i in range(a.shape[1] // 2)]
    return x, ys


def meas(out, key):
    """從 ngspice stdout 擷取 .meas 結果 key = value。"""
    for line in out.splitlines():
        s = line.strip().lower()
        if s.startswith(key.lower() + " ") or s.startswith(key.lower() + "="):
            try:
                return float(s.split("=")[1].split()[0])
            except Exception:
                return float("nan")
    return float("nan")
