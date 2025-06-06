# 新型光伏材料对气候影响的数值模拟

本项目旨在通过数值模拟，研究新型光伏材料对气候的影响。

## 项目结构

- `src/`: 存放模拟程序的核心源代码。
- `data/`: 存放输入数据，例如气象数据、光伏材料参数等。
- `results/`: 存放模拟输出结果。
- `scripts/`: 存放用于运行模拟、数据后处理和可视化的脚本。
- `doc/`: 存放项目相关文档。
- `requirements.txt`: 项目的 Python 依赖库列表。

## 如何开始

1.  **激活虚拟环境**:
    ```bash
    source venv/bin/activate
    ```
    *在 Windows 上, 使用 `venv\Scripts\activate`*

2.  **安装依赖 (在激活的虚拟环境中)**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **运行模拟**:
    ```bash
    python3 -m src.main
    ```
4.  **退出虚拟环境 (可选)**:
    ```bash
    deactivate
    ``` 

## 核心模型方程

本模拟包含两个核心部分：**局部气候效应**（由地表能量收支改变驱动）和**全球气候效应**（由替代化石燃料发电减少CO₂排放驱动）。

### 1. 局部温度变化 ($\Delta T_{\text{local}}$)

光伏板的部署改变了地表的反照率（Albedo）和能量转换路径，从而影响局部温度。我们通过计算地表净辐射通量的变化 ($\Delta R_{\text{net}}$) 来量化这一效应。

**a) 地表吸收的热量 (H_ground)**
在没有光伏板的情况下，地表吸收的太阳能并转化为热量的部分为：
$$ H_{\text{ground}} = I_{\text{solar}} \times (1 - \alpha_{\text{ground}}) $$
其中：
- $ I_{\text{solar}} $: 到达地表的太阳辐照度 (W/m²)
- $ \alpha_{\text{ground}} $: 地表原有的反照率

**b) 光伏板产生的废热 (H_panel)**
光伏板吸收的能量一部分转化为电能，其余则以废热形式耗散到环境中：
$$ H_{\text{panel}} = I_{\text{solar}} \times (1 - \alpha_{\text{panel}}) \times (1 - \eta_{\text{pv}}) $$
其中：
- $ \alpha_{\text{panel}} $: 光伏板的反照率
- $ \eta_{\text{pv}} $: 光伏板的发电效率

**c) 净辐射变化与温度异常**
局部环境净增加的热量 ($\Delta R_{\text{net}}$) 就是光伏板废热与地表原应吸收热量的差值：
$$ \Delta R_{\text{net}} = H_{\text{panel}} - H_{\text{ground}} $$
这个净增的能量通量通过一个气候敏感度参数 ($S_{\text{climate}}$) 转化为局部的温度变化 ($\Delta T_{\text{local}}$)：
$$ \Delta T_{\text{local}} = \Delta R_{\text{net}} \times S_{\text{climate}} $$
- $ S_{\text{climate}} $: 局部气候敏感度 (°C / (W/m²))

这个方程清晰地展示了"反照率效应"（由 $ \alpha_{\text{panel}} $ 和 $ \alpha_{\text{ground}} $ 的差异决定）和"废热效应"（由 $ \eta_{\text{pv}} $ 决定）如何共同作用，影响局部温度。

### 2. 全球温度变化 ($\Delta T_{\text{global}}$)

光伏发电可以替代传统的化石燃料发电，从而减少温室气体排放，对全球气候产生长期的降温效应。

**a) 总发电量 (E_total)**
在模拟周期（例如20年）内，光伏电站的总发电量为：
$$ E_{\text{total}} = P_{\text{total}} \times \text{Lifetime_hours} $$
其中 $ P_{\text{total}} $ 是电站的总装机容量。

**b) CO₂减排量 (CO2_reduced)**
总减排量由总发电量和电网的碳排放因子决定：
$$ \text{CO2}_{\text{reduced}} = E_{\text{total}} \times \text{EF}_{\text{grid}} $$
- $ \text{EF}_{\text{grid}} $: 电网平均碳排放因子 (kgCO₂/kWh)

**c) 全球温度变化**
我们使用"瞬态气候对累计碳排放的响应"（TCRE）来估算全球平均温度的变化：
$$ \Delta T_{\text{global}} = \frac{\text{CO2}_{\text{reduced}}}{10^{12}} \times \text{TCRE} $$
其中：
- CO₂减排量需要从kg转换为千兆吨 (Gt)。
- TCRE: 每排放1000 GtCO₂导致的全球平均温度上升值 (°C / 1000 GtCO₂)。

通过这个模型，我们可以量化和对比一个光伏项目在"局部增温"和"全球降温"两个维度上的影响。 