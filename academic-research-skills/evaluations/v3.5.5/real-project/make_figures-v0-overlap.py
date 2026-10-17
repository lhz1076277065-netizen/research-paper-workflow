from pathlib import Path
import json,numpy as np,pandas as pd
from reportlab.graphics.shapes import Drawing,Line,String,Circle,Rect,Polygon,PolyLine
from reportlab.graphics import renderPDF,renderSVG
from reportlab.lib.colors import HexColor,Color,black,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
P=Path(__file__).resolve().parent;F=P/'figures';F.mkdir(exist_ok=True)
font='/System/Library/Fonts/Supplemental/Arial.ttf';pdfmetrics.registerFont(TTFont('PlotArial',font))
d=pd.read_csv(P/'derived/wine.csv');e1=json.loads((P/'results/E1-v1.json').read_text());e2=json.loads((P/'results/E2-v1.json').read_text());m=json.loads((P/'results/models-v1.json').read_text())
W=468;H=252;cols={1:'#0072B2',2:'#D55E00',3:'#009E73'}
def text(dr,x,y,s,size=8,color=black,anchor='start'):
 dr.add(String(x,y,str(s),fontName='PlotArial',fontSize=size,fillColor=color,textAnchor=anchor))
def line(dr,x1,y1,x2,y2,color=black,width=.6,dash=None):
 dr.add(Line(x1,y1,x2,y2,strokeColor=color,strokeWidth=width,strokeDashArray=dash))
def marker(dr,x,y,c,r=1.8):
 co=HexColor(cols[c])
 if c==1:dr.add(Circle(x,y,r,fillColor=co,strokeColor=white,strokeWidth=.25))
 elif c==2:dr.add(Rect(x-r,y-r,2*r,2*r,fillColor=co,strokeColor=white,strokeWidth=.25))
 else:dr.add(Polygon([x,y+r*1.3,x-r*1.1,y-r,x+r*1.1,y-r],fillColor=co,strokeColor=white,strokeWidth=.25))
def axes(dr,box,xlim,ylim,xticks,yticks,xlab,ylab,title):
 l,b,w,h=box
 def fx(v):return l+(v-xlim[0])/(xlim[1]-xlim[0])*w
 def fy(v):return b+(v-ylim[0])/(ylim[1]-ylim[0])*h
 line(dr,l,b,l+w,b);line(dr,l,b,l,b+h)
 for v in xticks:line(dr,fx(v),b,fx(v),b-3);text(dr,fx(v),b-12,f'{v:g}',7.4,anchor='middle')
 for v in yticks:line(dr,l,fy(v),l-3,fy(v));text(dr,l-6,fy(v)-2.5,f'{v:g}',7.4,anchor='end')
 text(dr,l+w/2,b-27,xlab,8,anchor='middle');text(dr,l,b+h+10,title,9);text(dr,l,b+h+23,ylab,8)
 return fx,fy

def save(dr,name):
 renderPDF.drawToFile(dr,str(F/(name+'.pdf')));renderSVG.drawToFile(dr,str(F/(name+'.svg')))

fig=Drawing(W,H);fig.add(Rect(0,0,W,H,fillColor=white,strokeColor=None))
for i,c in enumerate([1,2,3]):marker(fig,52+i*125,237,c,2.3);text(fig,60+i*125,234,f'Class {c} (n={e2["groups"][str(c)]["n"]})',8)
fx,fy=axes(fig,(39,44,184,145),(11,15),(0,14),[11,12,13,14,15],[0,4,8,12],'Alcohol (recorded units)','Color intensity (recorded units)','a  Raw data and fitted lines')
for row in d.itertuples(index=False):marker(fig,fx(row.alcohol),fy(row.color_intensity),getattr(row,'_0') if hasattr(row,'_0') else int(row[0]))
for c,z in d.groupby('class'):
 b=m['class_'+str(c)]['beta'];xx=np.array([z.alcohol.min(),z.alcohol.max()]);line(fig,fx(xx[0]),fy(b[0]+b[1]*xx[0]),fx(xx[1]),fy(b[0]+b[1]*xx[1]),HexColor(cols[int(c)]),1.3,[3,2] if c==2 else ([1,2] if c==3 else None))
b=m['pooled']['beta'];xx=np.array([11,15]);line(fig,fx(xx[0]),fy(b[0]+b[1]*xx[0]),fx(xx[1]),fy(b[0]+b[1]*xx[1]),black,1.3,[5,3])
text(fig,42,15,'Dashed black: pooled OLS',7.6)
fx,fy=axes(fig,(278,44,177,145),(-1.6,1.6),(-5,6),[-1.5,0,1.5],[-4,-2,0,2,4,6],'Alcohol minus class mean','Color intensity minus class mean','b  Within-class-centered data')
xd=d.alcohol-d.groupby('class').alcohol.transform('mean');yd=d.color_intensity-d.groupby('class').color_intensity.transform('mean')
line(fig,fx(-1.6),fy(0),fx(1.6),fy(0),Color(.75,.75,.75),.5,[2,2]);line(fig,fx(0),fy(-5),fx(0),fy(6),Color(.75,.75,.75),.5,[2,2])
for xx,yy,c in zip(xd,yd,d['class']):marker(fig,fx(xx),fy(yy),int(c))
s=e2['adjusted_common_slope'];line(fig,fx(-1.6),fy(-1.6*s),fx(1.6),fy(1.6*s),black,1.4)
text(fig,279,15,f'Adjusted slope = {s:.3f}; partial r = {e2["partial_r_class_demeaned"]:.3f}',7.6)
save(fig,'figure1-associations')

fig=Drawing(W,180);fig.add(Rect(0,0,W,180,fillColor=white,strokeColor=None))
text(fig,15,165,'Recorded alcohol–color slopes: common direction, varying magnitudes',10)
left=118;right=454;bottom=40;top=142
fx=lambda v:left+v/3.05*(right-left)
line(fig,fx(0),bottom,fx(0),top,Color(.6,.6,.6),.6,[2,2]);line(fig,left,bottom,right,bottom)
for v in [0,.5,1,1.5,2,2.5,3]:line(fig,fx(v),bottom,fx(v),bottom-3);text(fig,fx(v),bottom-13,f'{v:g}',7.5,anchor='middle')
rows=[('Overall',e1['slope'],e1['slope_hc3_95'],black),*[(f'Class {c} (n={e2["groups"][str(c)]["n"]})',e2['groups'][str(c)]['slope'],e2['groups'][str(c)]['slope_hc3_95'],HexColor(cols[c])) for c in [1,2,3]],('Class-adjusted',s,e2['adjusted_slope_hc3_95'],black)]
for i,(lab,val,ci,col) in enumerate(rows):
 yy=top-8-i*21;text(fig,left-8,yy-2.5,lab,8,anchor='end');line(fig,fx(ci[0]),yy,fx(ci[1]),yy,col,1.3);line(fig,fx(ci[0]),yy-3,fx(ci[0]),yy+3,col,.8);line(fig,fx(ci[1]),yy-3,fx(ci[1]),yy+3,col,.8);fig.add(Circle(fx(val),yy,2.7,fillColor=col,strokeColor=white,strokeWidth=.4))
text(fig,(left+right)/2,10,'Color-intensity units per one recorded alcohol unit',8,anchor='middle')
save(fig,'figure2-slopes')

fig=Drawing(W,H);fig.add(Rect(0,0,W,H,fillColor=white,strokeColor=None))
for kind,box,title in [('pooled',(40,44,180,162),'a  Pooled OLS residuals'),('adjusted',(280,44,175,162),'b  Class-adjusted OLS residuals')]:
 mm=m[kind];fx,fy=axes(fig,box,(0,10),(-5,7),[0,2,4,6,8,10],[-4,-2,0,2,4,6],'Fitted color intensity','Residual (color units)',title)
 line(fig,fx(0),fy(0),fx(10),fy(0),Color(.6,.6,.6),.7,[3,2])
 for xx,yy,c in zip(mm['fitted'],mm['resid'],d['class']):marker(fig,fx(xx),fy(yy),int(c))
save(fig,'figureS1-residuals')
d[['class','alcohol','color_intensity']].assign(alcohol_centered=xd,color_centered=yd).to_csv(F/'figure-data.csv',index=False)
print('Wrote three editable SVG/vector PDF figures, fixed 6.5 inch width; main Figure1 height3.5, Figure2 height2.5 inches.')
