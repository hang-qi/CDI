v = load('seg.txt');
vt = load('seg_t.txt');

num_sent = sum(v);

seg = cumsum(v);
seg_t = cumsum(vt);

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

print('-depsc', 'test.eps');
print('-dpng', 'test.png');