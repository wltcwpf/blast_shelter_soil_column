import csv
import io
import json
from dataclasses import asdict, replace
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from model import Parameters, solve, sweep
from model_guide import render_guide

st.set_page_config(page_title='Hollow Soil Column', page_icon='🧱', layout='wide')
st.title('Hollow soil column under vertical load')
st.caption('Explore how soil, hoop membranes, and cavity air share an additional compression load.')

with st.sidebar:
    st.header('Specimen')
    H = st.number_input('Height (mm)', 20., 2000., 600., 10.)/1000
    ro = st.number_input('Outer radius (mm)', 5., 500., 300., 1.)/1000
    ri = st.number_input('Inner radius (mm)', 1., 499., 100., 1.)/1000
    st.header('Soil')
    Es = st.number_input('Soil modulus (MPa)', 0.01, 10000., 10., 0.5)*1e6
    nu = st.slider('Soil Poisson ratio', 0.0, 0.49, 0.30, 0.01)
    st.header('Inner membrane')
    Ei = st.number_input('Inner modulus (MPa)', 0.0, 100000., 1., 0.5)*1e6
    ti = st.number_input('Inner thickness (mm)', 0.0, 20., 0.5, 0.1)/1000
    st.header('Outer membrane')
    Eo = st.number_input('Outer modulus (MPa)', 0.0, 100000., 75000., 10.)*1e6
    to = st.number_input('Outer thickness (mm)', 0.0, 20., 0.5, 0.1)/1000
    st.header('Air and loading')
    sealed = st.radio('Air condition', ['Sealed, isothermal', 'Regulated, constant pressure']) == 'Sealed, isothermal'
    pg = st.number_input('Initial gauge pressure (kPa)', 0., 5000., 50., 10.)*1000
    patm = st.number_input('Atmospheric pressure (kPa)', 1., 200., 101.33, 1.)*1000
    maximum = st.number_input('Maximum additional force (N)', 1., 100000., 10000., 10.)
    fraction = st.slider('Applied load (% of maximum)', 0, 100, 100)
    scale = st.slider('Displacement exaggeration', 1, 100, 10)

p = Parameters(H,ri,ro,Es,nu,Ei,ti,Eo,to,pg,patm,sealed)
try:
    result = solve(p,maximum*fraction/100)
    data = sweep(p,maximum)
except (ValueError, np.linalg.LinAlgError) as exc:
    st.error(str(exc))
    st.stop()

st.info('Initial dimensions describe an already pressurized equilibrium. Load is the additional total force on a rigid plate spanning soil and air. The model does not calculate initial inflation.')
cols = st.columns(4)
cols[0].metric('Vertical shortening', f"{result['delta']*1000:.4f} mm")
cols[1].metric('Inner radial movement', f"{result['ui']*1000:+.4f} mm")
cols[2].metric('Outer radial movement', f"{result['uo']*1000:+.4f} mm")
cols[3].metric('Air gauge pressure', f"{result['p_gauge']/1000:.3f} kPa")
if not result['valid_geometry'] or result['p_abs'] <= 0:
    st.error('Nonphysical prediction: reduce the load. The linear model is outside its range.')
elif result['max_strain'] > 0.02 or abs(result['dV_ratio']) > 0.05:
    st.warning('Small-deformation range exceeded: strain > 2% or cavity-volume change > 5%. These are screening thresholds, not validated material limits.')
if ti/ri > 0.1 or to/ro > 0.1:
    st.warning('A membrane thickness exceeds 10% of its radius; the thin hoop-membrane approximation may be unsuitable.')

view, curves, theory = st.tabs(['Deformation', 'Load–response curves', 'Step-by-step model guide'])
with view:
    left,right = st.columns([1.5,1])
    display_scale = scale
    if H-scale*result['delta'] <= 0 or not (0 < ri+scale*result['ui'] < ro+scale*result['uo']):
        display_scale = 1
        st.warning('Exaggeration would distort the geometry; displaying actual deformation instead.')
    h1 = (H-display_scale*result['delta'])*1000
    r1 = (ri+display_scale*result['ui'])*1000
    r2 = (ro+display_scale*result['uo'])*1000
    fig = go.Figure()
    def rectangle(x0,x1,height,name,color,fill=False,dash=None):
        fig.add_trace(go.Scatter(x=[x0,x1,x1,x0,x0],y=[0,0,height,height,0],
            mode='lines', name=name, line=dict(color=color,dash=dash),
            fill='toself' if fill else None, opacity=0.65 if fill else 1))
    rectangle(-ri*1000,ri*1000,H*1000,'Initial cavity','#64748b',dash='dash')
    rectangle(-ro*1000,ro*1000,H*1000,'Initial outer boundary','#94a3b8',dash='dash')
    rectangle(-r1,r1,h1,'Air','#38bdf8',True)
    rectangle(-r2,-r1,h1,'Soil, left','#b88652',True)
    rectangle(r1,r2,h1,'Soil, right','#b88652',True)
    for radius,color,name in [(r1,'#06b6d4','Inner membrane'),(r2,'#334155','Outer membrane')]:
        fig.add_trace(go.Scatter(x=[-radius,-radius,None,radius,radius],y=[0,h1,None,0,h1],
            mode='lines',line=dict(color=color,width=4),name=name))
    fig.add_trace(go.Scatter(x=[-r2,r2],y=[h1,h1],mode='lines',line=dict(color='#111827',width=8),name='Top plate'))
    fig.add_annotation(x=0,y=h1,text=f'↓ {maximum*fraction/100:.1f} N additional load',showarrow=False,yshift=22)
    fig.update_layout(height=560,xaxis_title='Radial position (mm)',yaxis_title='Height (mm)',
        yaxis=dict(scaleanchor='x',scaleratio=1),margin=dict(t=45,b=20),legend=dict(orientation='h',y=-0.18))
    left.plotly_chart(fig,width='stretch')
    right.markdown(f'**Displayed displacement scale: {display_scale}×**\n\nBlue is the air cavity; brown is soil. Dashed lines show initial geometry.\n\nPositive radial movement is outward. All reported values use actual displacement.')
    right.metric('Axial compressive strain',f"{100*result['delta']/H:.3f}%")
    right.metric('Linearized cavity volume change',f"{100*result['dV_ratio']:+.3f}%")
    right.metric('Apparent axial stiffness',f"{1/solve(p,1)['delta']/1000:.2f} N/mm")
    radial = go.Figure(go.Scatter(x=result['r']*1000,y=result['ur']*1000,mode='lines'))
    radial.update_layout(xaxis_title='Original radius (mm)',yaxis_title='Radial displacement (mm)',height=300)
    st.plotly_chart(radial,width='stretch')
with curves:
    compare = st.checkbox('Compare sealed air with regulated pressure',value=True)
    alternate = sweep(replace(p,sealed=not sealed),maximum) if compare else None
    current_name = 'Sealed air' if sealed else 'Regulated pressure'
    for keys,title,unit in [(['shortening_mm'],'Vertical shortening','mm'),
                            (['inner_displacement_mm','outer_displacement_mm'],'Radial displacement','mm'),
                            (['pressure_gauge_kPa'],'Air gauge pressure','kPa')]:
        fig = go.Figure()
        for key in keys:
            label = key.replace('_',' ').replace(' mm','').replace(' kPa','')
            fig.add_trace(go.Scatter(x=data['force_N'],y=data[key],name=f'{label}: {current_name}'))
            if alternate is not None:
                fig.add_trace(go.Scatter(x=alternate['force_N'],y=alternate[key],
                    name=f'{label}: alternative',line=dict(dash='dash')))
        fig.add_vline(x=maximum*fraction/100,line_dash='dot',line_color='gray')
        fig.update_layout(title=title,xaxis_title='Additional force (N)',yaxis_title=unit,height=320)
        st.plotly_chart(fig,width='stretch')
    peak = solve(p,maximum)
    if peak['max_strain']>0.02 or abs(peak['dV_ratio'])>0.05 or not peak['valid_geometry'] or peak['p_abs']<=0:
        st.warning('The upper part of this sweep exceeds the model screening limits. Lower the maximum force.')
    out=io.StringIO()
    writer=csv.writer(out)
    writer.writerow(data.keys())
    writer.writerows(zip(*data.values()))
    st.download_button('Download load sweep CSV',out.getvalue(),'load_sweep.csv','text/csv')
    st.download_button('Download parameter JSON',json.dumps(asdict(p),indent=2),'parameters.json','application/json')
with theory:
    render_guide(p, result, maximum*fraction/100)
