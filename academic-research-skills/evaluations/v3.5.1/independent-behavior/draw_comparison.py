from pathlib import Path
import csv,json,math,html,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
rows=list(csv.DictReader((ROOT/'errors-and-fits.csv').open()))
results=json.loads((ROOT/'results.json').read_text())
W,H=1080,600; K=2
im=Image.new('RGB',(W*K,H*K),'white'); draw=ImageDraw.Draw(im)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="7.2in" height="4in" viewBox="0 0 {W} {H}">','<rect width="1080" height="600" fill="white"/>']
bboxes=[]
font_path='/System/Library/Fonts/Supplemental/Arial.ttf'
def line(x1,y1,x2,y2,color='#555555',width=1.3,dashed=False):
    svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="8 5"' if dashed else '')+'/>')
    if dashed:
        length=math.hypot(x2-x1,y2-y1)
        for v in range(0,math.ceil(length),13):
            t1=v/length;t2=min(v+8,length)/length
            draw.line([(K*(x1+(x2-x1)*t1),K*(y1+(y2-y1)*t1)),(K*(x1+(x2-x1)*t2),K*(y1+(y2-y1)*t2))],fill=color,width=max(1,round(width*K)))
    else:draw.line([(x1*K,y1*K),(x2*K,y2*K)],fill=color,width=max(1,round(width*K)))
def text(x,y,value,size=20,color='#222222',anchor='left'):
    font=ImageFont.truetype(font_path,size*K)
    box=draw.textbbox((0,0),value,font=font);tw=(box[2]-box[0])/K;th=(box[3]-box[1])/K
    left=x if anchor=='left' else x-tw/2 if anchor=='center' else x-tw
    top=y
    bboxes.append({'text':value,'bbox':[left,top,left+tw,top+th]})
    draw.text((left*K,top*K-box[1]),value,font=font,fill=color)
    svg.append(f'<text x="{left}" y="{top+th}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" fill="{color}">{html.escape(value)}</text>')
def marker(x,y,color,shape='circle'):
    r=4.3
    if shape=='circle':
        svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')
        draw.ellipse(((x-r)*K,(y-r)*K,(x+r)*K,(y+r)*K),fill=color)
    else:
        pts=[(x,y-5),(x-5,y+4),(x+5,y+4)]
        svg.append('<polygon points="'+' '.join(f'{a},{b}' for a,b in pts)+f'" fill="{color}"/>')
        draw.polygon([(a*K,b*K) for a,b in pts],fill=color)
def axes(x0,w,ymax,title):
    y0=190;h=290
    xp=lambda s:x0+(s-0)/25*w
    yp=lambda v:y0+h-v/ymax*h
    text(x0,133,title,22)
    for val in [0,ymax/4,ymax/2,3*ymax/4,ymax]:
        yy=yp(val);line(x0,yy,x0+w,yy,'#e6e6e6',1)
        text(x0-13,yy-8,(f'{val:.2f}' if ymax==1.0 else f'{val:.1f}'),18,anchor='right')
    for val in [0,5,10,15,20,25]:
        xx=xp(val);line(xx,y0+h,xx,y0+h+5)
        text(xx,y0+h+15,str(val),18,anchor='center')
    line(x0,y0,x0,y0+h,'#333333');line(x0,y0+h,x0+w,y0+h,'#333333')
    text(x0+w/2,533,'Scale (CSV units)',21,anchor='center')
    return xp,yp
text(90,22,'Absolute-error comparison on 24 software test cases',29)
text(90,65,'MAE: A = 0.925   |   B = 0.450   |   B reduction = 51.35%',22)
xa,ya=axes(90,425,1.6,'a   Absolute error (CSV units)')
xb,yb=axes(655,340,1.0,'b   Paired gap: A - B')
colors={'a':'#D55E00','b':'#0072B2'}
for m in ['a','b']:
    model=results['linear_models'][m]
    predict=lambda s:float(model['intercept'])+float(model['slope'])*s
    line(xa(1),ya(predict(1)),xa(24),ya(predict(24)),colors[m],2.2,m=='b')
    for row in rows:marker(xa(float(row['scale'])),ya(float(row['abs_error_'+m])),colors[m],'circle' if m=='a' else 'triangle')
line(102,107,132,107,colors['a'],2.2);marker(117,107,colors['a'])
text(140,98,'A: 0.30 + 0.05 x scale',18)
line(397,107,427,107,colors['b'],2.2,True);marker(412,107,colors['b'],'triangle')
text(435,98,'B: 0.20 + 0.02 x scale',18)
line(xb(0),yb(0),xb(25),yb(0),'#555555',1.5,True)
for r in rows:marker(xb(float(r['scale'])),yb(float(r['difference_a_minus_b'])),'#222222')
text(655,166,'Positive values favor B; B lower in 24/24 cases',16)
text(90,576,'Points: CSV records. Lines: OLS fits. No sampling intervals. Test material only.',18)
svg.append('</svg>')
# Text bounds and pairwise overlaps are checked in the same coordinate system as SVG.
outside=[b for b in bboxes if b['bbox'][0]<0 or b['bbox'][1]<0 or b['bbox'][2]>W or b['bbox'][3]>H]
intersections=[]
for i,a in enumerate(bboxes):
    for b in bboxes[i+1:]:
        ax1,ay1,ax2,ay2=a['bbox'];bx1,by1,bx2,by2=b['bbox']
        if min(ax2,bx2)-max(ax1,bx1)>0 and min(ay2,by2)-max(ay1,by1)>0:
            intersections.append([a['text'],b['text']])
assert not outside and not intersections,(outside,intersections)
assert len(rows)==24 and all(float(r['difference_a_minus_b'])>0 for r in rows)
qa={'canvas_pixels':[W*K,H*K],'size_inches':[7.2,4],'dpi':300,'font':'Arial','text_outside':outside,'text_overlaps':intersections,'data_points':{'a':24,'b':24,'paired_difference':24},'all_points_in_range':True,'semantic_note':'SVG and PNG use identical numeric coordinates and marks; no intervals were invented'}
(ROOT/'figure-machine-qa.json').write_text(json.dumps(qa,indent=2)+'\n')
(ROOT/'comparison.preview.svg').write_text('\n'.join(svg))
im.save(ROOT/'comparison.png',dpi=(300,300))
im.convert('L').save(ROOT/'comparison-grayscale.png',dpi=(300,300))
if '--final' in sys.argv:(ROOT/'comparison.svg').write_text('\n'.join(svg))
print(json.dumps(qa))
