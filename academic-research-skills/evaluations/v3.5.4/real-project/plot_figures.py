import argparse,csv,json,pathlib,html
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
R=pathlib.Path(__file__).resolve().parent;F=R/'figures';F.mkdir(exist_ok=True)
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
pdfmetrics.registerFont(TTFont('StudyArial',FONT))
BLUE='#0072B2';ORANGE='#D55E00';BLACK='#202730';GREY='#E2E6EA'
class Scene:
    def __init__(self,h):self.w=432;self.h=h;self.items=[];self.checks=[]
    def text(self,x,y,s,size=8,anchor='start',color=BLACK):
        width=pdfmetrics.stringWidth(s,'StudyArial',size);left=x if anchor=='start' else x-width if anchor=='end' else x-width/2
        assert 0<=left and left+width<=self.w and size<=y<=self.h,(s,left,width)
        self.items.append(('text',(x,y,s,size,anchor,color)));self.checks.append({'text':s,'left':left,'right':left+width,'top':y-size,'bottom':y})
    def line(self,x1,y1,x2,y2,color=GREY,width=.6):self.items.append(('line',(x1,y1,x2,y2,color,width)))
    def point(self,x,y,color=BLUE,shape='circle',radius=1.4):
        assert radius<x<self.w-radius and radius<y<self.h-radius
        self.items.append(('point',(x,y,color,shape,radius)))
    def save(self,name,final):
        scale=300/72;im=Image.new('RGB',(round(self.w*scale),round(self.h*scale)),'white');draw=ImageDraw.Draw(im)
        svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="6in" height="{self.h/72}in" viewBox="0 0 {self.w} {self.h}">','<rect width="100%" height="100%" fill="white"/>']
        c=canvas.Canvas(str(F/(name+'.pdf')),pagesize=(self.w,self.h)) if final else None
        for kind,args in self.items:
            if kind=='text':
                x,y,s,size,anchor,color=args;font=ImageFont.truetype(FONT,round(size*scale));anc={'start':'ls','end':'rs','middle':'ms'}[anchor]
                draw.text((x*scale,y*scale),s,font=font,fill=color,anchor=anc)
                svg.append(f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" text-anchor="{anchor}" fill="{color}">{html.escape(s)}</text>')
                if c:
                    c.setFillColor(color);c.setFont('StudyArial',size)
                    {'start':c.drawString,'end':c.drawRightString,'middle':c.drawCentredString}[anchor](x,self.h-y,s)
            elif kind=='line':
                x1,y1,x2,y2,color,width=args;draw.line((x1*scale,y1*scale,x2*scale,y2*scale),fill=color,width=max(1,round(width*scale)))
                svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>')
                if c:c.setStrokeColor(color);c.setLineWidth(width);c.line(x1,self.h-y1,x2,self.h-y2)
            else:
                x,y,color,shape,rad=args;box=((x-rad)*scale,(y-rad)*scale,(x+rad)*scale,(y+rad)*scale)
                (draw.ellipse if shape=='circle' else draw.rectangle)(box,fill=color)
                svg.append(f'<circle cx="{x}" cy="{y}" r="{rad}" fill="{color}"/>' if shape=='circle' else f'<rect x="{x-rad}" y="{y-rad}" width="{2*rad}" height="{2*rad}" fill="{color}"/>')
                if c:
                    c.setFillColor(color)
                    if shape=='circle':c.circle(x,self.h-y,rad,stroke=0,fill=1)
                    else:c.rect(x-rad,self.h-y-rad,2*rad,2*rad,stroke=0,fill=1)
        if not final:
            im.save(F/(name+'.png'),dpi=(300,300));ImageOps.grayscale(im).save(F/(name+'-grayscale.png'),dpi=(300,300))
        else:
            svg.append('</svg>');(F/(name+'.svg')).write_text('\n'.join(svg));c.save()
        return {'name':name,'width_inches':6,'height_inches':self.h/72,'minimum_text_pt':min(a[3] for k,a in self.items if k=='text'),'text_bounds_passed':True,'texts':self.checks,'plotted_point_count':sum(k=='point' for k,a in self.items)}

def main(final):
    records=list(csv.DictReader((R/'results'/'results.csv').open()));rows=[];audit=[]
    arms=['majority','centroid_raw','centroid_scaled','knn5_raw','knn5_scaled'];labels=['Majority','Centroid | raw','Centroid | scaled','5-NN | raw','5-NN | scaled']
    sc=Scene(336);sc.text(12,17,'A  Fixed classifiers: scaling effects differ by dataset',10);sc.text(12,32,'Dots = 30 dependent holdouts per arm; black ticks = descriptive means',7.5)
    for name,top,title in [('wine',65,'Wine: 178 rows'),('iris',213,'Iris: 150 rows')]:
        sc.text(12,top-15,title,9)
        for v in np.linspace(0,1,6):
            x=116+v*296;sc.line(x,top-6,x,top+83);sc.text(x,top+99,str(round(100*v)),7.5,anchor='middle')
        for k,(arm,label) in enumerate(zip(arms,labels)):
            yy=top+18*k;sc.text(109,yy+2.5,label,7.5,anchor='end')
            values=sorted([r for r in records if r['dataset']==name and r['arm']==arm],key=lambda r:int(r['seed']))
            for r in values:
                v=float(r['balanced_accuracy']);jit=((int(r['seed'])*7)%13-6)*.65
                sc.point(116+v*296,yy+jit,ORANGE if arm.endswith('scaled') else BLUE,'square' if arm.endswith('scaled') else 'circle')
                rows.append({'figure':'scores','dataset':name,'arm':arm,'seed':int(r['seed']),'test_fraction':.2,'value':v})
            mean=np.mean([float(r['balanced_accuracy']) for r in values]);sc.line(116+mean*296,yy-5,116+mean*296,yy+5,BLACK,1.3)
    sc.text(263,333,'Balanced accuracy (%)',8,anchor='middle');audit.append(sc.save('figure1',final))
    effect=Scene(238);effect.text(12,17,'B  Paired scaling change is stable across test fractions',10)
    effect.point(20,34,BLUE);effect.text(28,37,'20% test',7.5);effect.point(105,34,ORANGE,'square');effect.text(113,37,'30% test',7.5);effect.text(210,37,'Each dot = one matched split',7.5)
    xmap=lambda v:116+(v+.25)/.7*296
    for v in (-.2,0,.2,.4):effect.line(xmap(v),48,xmap(v),191,BLACK if v==0 else GREY,.8 if v==0 else .6);effect.text(xmap(v),207,str(round(100*v)),7.5,anchor='middle')
    for i,(name,family) in enumerate([('wine','centroid'),('wine','knn5'),('iris','centroid'),('iris','knn5')]):
        yy=66+34*i;effect.text(109,yy+2.5,name.title()+' | '+('5-NN' if family=='knn5' else 'centroid'),7.5,anchor='end')
        for fraction,folder,dy,color,shape in [(.2,'results',-4,BLUE,'circle'),(.3,'sensitivity',4,ORANGE,'square')]:
            rr=list(csv.DictReader((R/folder/'results.csv').open()))
            raw={int(r['seed']):float(r['balanced_accuracy']) for r in rr if r['dataset']==name and r['arm']==family+'_raw'}
            vals={int(r['seed']):float(r['balanced_accuracy']) for r in rr if r['dataset']==name and r['arm']==family+'_scaled'}
            for seed in range(30):
                value=vals[seed]-raw[seed];assert -.25<=value<=.45
                effect.point(xmap(value),yy+dy+((seed*7)%9-4)*.5,color,shape)
                rows.append({'figure':'paired_change','dataset':name,'arm':family,'seed':seed,'test_fraction':fraction,'value':value})
    effect.text(263,225,'Scaled minus raw balanced accuracy (percentage points)',7.5,anchor='middle');audit.append(effect.save('figure2',final))
    if not final:
        with (F/'plot-data.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        (F/'layout-audit.json').write_text(json.dumps(audit,indent=2))
    print(json.dumps([{'figure':a['name'],'points':a['plotted_point_count'],'bounds':a['text_bounds_passed']} for a in audit]))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');main(p.parse_args().final)
