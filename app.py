import streamlit as st
import math

# 设置网页标题和布局宽度
st.set_page_config(page_title="好坏腔双波长主动光钟计算器", layout="wide")

st.title("原子好坏腔双波长主动光频标")
st.markdown("理论极限设计与参数寻优 (网页计算版)")

# ==================== 【侧边栏：输入参数】 ====================
st.sidebar.header("参数设置")

P_pump_mW = st.sidebar.number_input("459nm 泵浦光功率 (mW)", min_value=1.0, max_value=100.0, value=20.0, step=1.0)
L = st.sidebar.number_input("物理腔长 (m)", min_value=0.01, max_value=2.0, value=0.3, step=0.01)
T_pass2 = st.sidebar.number_input("气室两次透射率乘积", min_value=0.1, max_value=1.0, value=0.96, step=0.01)

st.sidebar.markdown("---")
st.sidebar.subheader("腔镜反射率设置")
R_1359_set = st.sidebar.number_input("1359nm 反射率 (R)", min_value=0.01, max_value=0.9999, value=0.99, step=0.001, format="%.4f")
R_1470_set = st.sidebar.number_input("1470nm 反射率 (R)", min_value=0.01, max_value=0.9999, value=0.50, step=0.01)

# ==================== 【后台物理计算引擎】 ====================
# 1. 基本物理常数
c = 2.9979e8
amu = 1.6605e-27
m_Cs = 132.9 * amu
P_pump = P_pump_mW * 1e-3
lambda_459 = 459.3e-9
lambda_1359 = 1359.2e-9
lambda_1470 = 1469.9e-9

# 2. 衰减率与退相干率
Gamma_7P1_2 = 6.4e6
Gamma_7S1_2 = 2.08e7
Gamma_6P3_2 = 3.3e7
Gamma_6P1_2 = 2.8e7
Gamma_6S1_2 = 0
gamma_52 = 0.5 * (Gamma_7S1_2 + Gamma_6P1_2)
gamma_53 = 0.5 * (Gamma_7S1_2 + Gamma_6P3_2)
gamma_61 = 0.5 * (Gamma_7P1_2 + Gamma_6S1_2)

# 3. 线宽计算
Area_pump = math.pi * (0.5e-3)**2
I_pump = P_pump / Area_pump
I_sat_459 = 13.8
S_pump = I_pump / I_sat_459
Gamma_s_459 = (gamma_61 / math.pi) * math.sqrt(1 + S_pump)
v_lim = Gamma_s_459 * lambda_459 / 2

Delta_nu_D_1359 = 2 * v_lim / lambda_1359
Delta_nu_D_1470 = 2 * v_lim / lambda_1470
f_L_1359 = gamma_52 / math.pi
f_L_1470 = gamma_53 / math.pi

linewidth_g_1359 = 0.5346 * f_L_1359 + math.sqrt(0.2166 * f_L_1359**2 + Delta_nu_D_1359**2)
linewidth_g_1470 = 0.5346 * f_L_1470 + math.sqrt(0.2166 * f_L_1470**2 + Delta_nu_D_1470**2)

# 4. 腔参数计算
FSR = c / (2 * L)
R_eff_1359 = math.sqrt(R_1359_set**2) * T_pass2
Finese_1359 = math.pi / math.acos(2*R_eff_1359 / (1 + R_eff_1359**2))
linewidth_c_1359 = FSR / Finese_1359

R_eff_1470 = math.sqrt(R_1470_set**2) * T_pass2
Finese_1470 = math.pi / math.acos(2*R_eff_1470 / (1 + R_eff_1470**2))
linewidth_c_1470 = FSR / Finese_1470

# 5. 坏腔系数
a_1359_val = linewidth_c_1359 / linewidth_g_1359
a_1470_val = linewidth_c_1470 / linewidth_g_1470

# ==================== 【主界面：结果展示】 ====================
st.subheader("【物理参数输出】")
col1, col2 = st.columns(2)
with col1:
    st.info(f"**1359nm 增益线宽:** {linewidth_g_1359/1e6:.2f} MHz \n\n (自然宽 {f_L_1359/1e6:.1f} + 多普勒 {Delta_nu_D_1359/1e6:.1f})")
with col2:
    st.info(f"**1470nm 增益线宽:** {linewidth_g_1470/1e6:.2f} MHz \n\n (自然宽 {f_L_1470/1e6:.1f} + 多普勒 {Delta_nu_D_1470/1e6:.1f})")

st.markdown("---")
st.subheader(f"【特定反射率测试 (R_1359={R_1359_set}, R_1470={R_1470_set})】")

# 使用 Metrics 面板展示核心结果，一目了然
col3, col4, col5 = st.columns(3)
with col3:
    st.metric(label="1359nm 精细度", value=f"{Finese_1359:.2f}")
    st.metric(label="1470nm 精细度", value=f"{Finese_1470:.2f}")
with col4:
    st.metric(label="1359nm 腔模线宽", value=f"{linewidth_c_1359/1e6:.2f} MHz")
    st.metric(label="1470nm 腔模线宽", value=f"{linewidth_c_1470/1e6:.2f} MHz")
with col5:
    # 坏腔系数 a 极其重要，做特殊标红或标绿处理 (此处利用st.metric的delta)
    st.metric(label="1359nm 坏腔系数 a", value=f"{a_1359_val:.3f}")
    st.metric(label="1470nm 坏腔系数 a", value=f"{a_1470_val:.3f}")