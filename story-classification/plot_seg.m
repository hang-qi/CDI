v = load('output/seg.txt');
vt = load('output/seg_t.txt');

num_sent = sum(v);

seg = cumsum(v);
seg_t = cumsum(vt);

seg = [0 seg];
seg_t = [0 seg_t];

figure;
plot(seg, 0.2*ones(1,size(seg,2)), '+-', 'DisplayName', 'Segment Result', ...
    'LineWidth', 1, 'MarkerSize', 10);
hold on;
plot(seg_t, zeros(1,size(seg_t,2)), '+-r', 'DisplayName', 'Ground Truth', ...
    'LineWidth', 1, 'MarkerSize', 10);
grid on;
legend('Segmentation Result','Ground Truth');
%legend('show');
axis([-10 num_sent+10 -0.2 0.6]);

print('-depsc', 'output/test.eps');
print('-dpng', 'output/test.png');