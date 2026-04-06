# N-Body Simulator（簡易 N 體模擬系統）

本專案為一個用於模擬多個物體之間 **重力交互作用與碰撞** 的系統，並提供圖形化介面與模擬回放功能。



---

## 專題特色

-  模擬多體重力（N-body problem）
-  支援物體碰撞
-  圖形化操作介面（Tkinter）
-  模擬結果回放
-  模擬資料上傳 / 下載
-  支援 NumPy / CuPy / C++ 加速

---

## 使用技術

### Simulation / Frontend
- Python
- Tkinter
- VPython
- NumPy
- CuPy (optional)

### 後端
- Flask
- MySQL
- HTTP File Server

## 效能優化(進行中)

目前專案正在進行效能優化：

- 使用 **CMake** 管理 C++ 編譯流程
- 將核心計算（如重力計算）改由 **C++ 執行**
- 使用 **pybind11** 與 Python 整合
-  **計畫加入 Barnes-Hut 演算法**

---
## Demo

<p align="center">
  <img src="images/Architecture.png" width="600"/>
  <br>
  <em>圖1：N-body 系統架構</em>
</p>

<p align="center">
  <img src="images/gui.png" width="600"/>
  <br>
  <em>圖2：參數設定介面</em>
</p>


<p align="center">
  <img src="images/gui(2).png" width="600"/>
  <br>
  <em>圖2：參數設定介面(2)</em>
</p>


















