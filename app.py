import streamlit as st
import math

# 设置网页标题和布局宽度
st.set_page_config(page_title="好坏腔双波长主动光钟计算器", layout="wide")

st.title("原子好坏腔双波长主动光频标")
st.markdown("理论极限设计与参数寻优 (网页计算版)")

# ==================== 【侧边栏：输入参数】 ====================
st.sidebar.header("参数设置")

P_pump_mW = st.sidebar.number_input("泵浦光功率 (mW)", min_value=1.0, max_value=200.0, value=20.0, step=1.0)
r_pump_mm = st.sidebar.number_input("泵浦光斑半径 (mm)", min_value=0.1, max_value=5.0, value=0.5, step=0.1, help="用于计算泵浦光光强")
L = st.sidebar.number_input("物理腔长 L (m)", min_value=0.01, max_value=2.0, value=0.30, step=0.01)
T_pass2 = st.sidebar.number_input("气室透过率", min_value=0.1, max_value=1.0, value=0.96, step=0.01)

st.sidebar.markdown("---")
st.sidebar.subheader("腔镜反射率设置")
R_1359_set = st.sidebar.number_input("1359nm 反射率 (R1=R2)", min_value=0.01, max_value=0.9999, value=0.9900, step=0.001, format="%.4f")
R_1470_set = st.sidebar.number_input("1470nm 反射率 (R1=R2)", min_value=0.01, max_value=0.9999, value=0.5000, step=0.01)

# ==================== 【后台物理计算引擎】 ====================
# 1. 基本物理常数
c = 2.9979e8
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

# 3. 泵浦光强与线宽计算
P_pump = P_pump_mW * 1e-3
Area_pump = math.pi * (r_pump_mm * 1e-3)**2             
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

# 5. 坏腔系数与腔牵引系数
a_1359_val = linewidth_c_1359 / linewidth_g_1359
a_1470_val = linewidth_c_1470 / linewidth_g_1470

P_1359_val = 1 / (1 + a_1359_val)
P_1470_val = 1 / (1 + a_1470_val)

# ==================== 【主界面：结果展示】 ====================
st.subheader("【好坏腔系数和腔牵引系数】")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="1359nm 坏腔系数 a", value=f"{a_1359_val:.3f}")
with col2:
    st.metric(label="1359nm 腔牵引系数 P", value=f"{P_1359_val:.3f}")
with col3:
    st.metric(label="1470nm 坏腔系数 a", value=f"{a_1470_val:.3f}")
with col4:
    st.metric(label="1470nm 腔牵引系数 P", value=f"{P_1470_val:.3f}")

st.markdown("---")
st.subheader(f"【腔参数评估 (R_1359={R_1359_set}, R_1470={R_1470_set})】")

st.markdown("#### 1359nm 腔参数")
c1, c2, c3 = st.columns(3)
with c1:
    st.info(f"**增益线宽:** {linewidth_g_1359/1e6:.2f} MHz \n\n (自然宽 {f_L_1359/1e6:.1f} + 多普勒 {Delta_nu_D_1359/1e6:.1f})")
with c2:
    st.info(f"**腔模线宽:** {linewidth_c_1359/1e6:.2f} MHz")
with c3:
    st.info(f"**腔精细度:** {Finese_1359:.2f} (无量纲)")

st.markdown("#### 1470nm 腔参数")
c4, c5, c6 = st.columns(3)
with c4:
    st.info(f"**增益线宽:** {linewidth_g_1470/1e6:.2f} MHz \n\n (自然宽 {f_L_1470/1e6:.1f} + 多普勒 {Delta_nu_D_1470/1e6:.1f})")
with c5:
    st.info(f"**腔模线宽:** {linewidth_c_1470/1e6:.2f} MHz")
with c6:
    st.info(f"**腔精细度:** {Finese_1470:.2f} (无量纲)")

st.markdown("---")
st.subheader("【泵浦光参数】")
st.info(f"**泵浦光光强 (I_pump):** {I_pump:.2f} W/m²")
