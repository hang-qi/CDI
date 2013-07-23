clear all

[ likelihood, intra_class_similarity, inter_class_distance, length ] = data();

% Ground Truth Data
likelihood_gt = 7051.4376;
intra_gt = 5.2366;
inter_gt = 36.998035;
len_gt = 14;

likelihood = likelihood - likelihood_gt;
intra_class_similarity = intra_class_similarity - intra_gt;
inter_class_distance = inter_class_distance - inter_gt;
length = length - len_gt;

A = [likelihood, intra_class_similarity, inter_class_distance, length];

m = 4;
v = ones(1,m);
cvx_begin
    variables w(m)   
    minimize( norm(A*w) )
    subject to
%         A*w > 0
        v*w == 1
        w > 0
cvx_end