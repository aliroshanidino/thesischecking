import sys; sys.path.insert(0, '.')
from eqkit import eq_png
A = r'\color{#B7791A}'
E = {
 'izh': r'\begin{aligned}\frac{dv}{dt}&=0.04\,v^{2}+5v+140-u+I\\[4pt]\frac{du}{dt}&=a\,(b\,v-u)\\[4pt]v\ge 30\ \text{mV}\ &\Rightarrow\ v\leftarrow c,\quad u\leftarrow u+d\end{aligned}',
 'map': r'V=\frac{v+65}{64},\qquad U=\frac{u}{64},\qquad I_{hw}=\frac{I}{64}',
 'hw':  r'\begin{aligned}\frac{dV}{dt}&=2.56\,V^{2}-0.2\,V+I_{hw}-U-0.25\\[4pt]\frac{dU}{dt}&=a\Big(b\,V-U-\tfrac{65b}{64}\Big)\end{aligned}',
 'hasizh': r'\begin{aligned}\frac{dV}{dt}&=2.56\,V^{2}-0.2\,V+I_{hw}-U-0.25\\[3pt]\frac{dU}{dt}&=a\Big(b\,V-U-\tfrac{65b}{64}\Big)\\[3pt]' + A + r'{\frac{d\theta}{dt}}&\mathrel{' + A + r'{=}}' + A + r'{\alpha\,(\theta_0-\theta)+\gamma\textstyle\sum_k\delta(t-t_k)}\\[3pt]V\ge' + A + r'{\theta}\ &\Rightarrow\ V\leftarrow c_{hw},\ \ U\leftarrow U+d_{hw}+' + A + r'{\beta\,(\theta-\theta_0)}\end{aligned}',
 'lyap': r'\begin{aligned}\mathcal{V}(\theta)&=\tfrac12\,(\theta-\theta^{*})^{2}\\[3pt]\dot{\mathcal V}&=(\theta-\theta^{*})\big[-\alpha(\theta-\theta^{*})+\gamma\,(r-r^{*})\big]<0\\[3pt]&\Rightarrow\ |\theta-\theta^{*}|\lesssim\gamma\quad\text{(UUB)}\end{aligned}',
 'ours': r'\frac{d\theta}{dt}=\underbrace{\alpha\,(\theta_0-\theta)}_{\text{leak}}+\underbrace{\gamma\textstyle\sum_k\delta(t-t_k)}_{\text{per-spike step}},\qquad \text{spike if } V\ge\theta',
 'dc':   r'\frac{d\theta_{\!e}}{dt}=\underbrace{\tfrac{1}{\tau_\theta}\,(v_{th}-\theta_{\!e})}_{\text{leak}}+\underbrace{\theta^{+}\textstyle\sum_k\delta(t-t_k)}_{\text{per-spike step}},\qquad \text{spike if } v\ge\theta_{\!e}',
 'map2': r'\alpha\;\leftrightarrow\;\tfrac{1}{\tau_\theta}\qquad\quad \theta_0\;\leftrightarrow\;v_{th}\qquad\quad \gamma\;\leftrightarrow\;\theta^{+}',
 'pwl':  r'\mathrm{PWL}(V)=\begin{cases}0 & V<0\\ V\gg1 & 0\le V<0.25\\ (V\ll1)-0.375 & 0.25\le V<0.625\\ (V\ll2)-1.625 & 0.625\le V<1.125\\ (V\ll3)-6.125 & V\ge1.125\end{cases}\ \approx\ 2.56\,V^{2}',
}
for k, t in E.items():
    eq_png(t, f'figs/eq/{k}.png', 40); print('ok', k)
