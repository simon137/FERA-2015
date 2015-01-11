# The SVM baseline for BO4D
import shared_defs_BP4D
import data_preparation
import numpy

import mlp

(all_aus, train_recs, devel_recs, BP4D_dir, hog_data_dir) = shared_defs_BP4D.shared_defs()

pca_loc = "../pca_generation/generic_face_rigid"

f = open("./trained/BP4D_train_mlp_joint.txt", 'w')

# load the training and testing data for the current fold
[train_samples, train_labels, valid_samples, valid_labels, raw_valid, PC, means, scaling] = \
    data_preparation.Prepare_HOG_AU_data_generic_BP4D(train_recs, devel_recs, all_aus, BP4D_dir, hog_data_dir, pca_loc)

import validation_helpers

train_fn = mlp.train_mlp
test_fn = mlp.test_mlp

hyperparams = {
   'batch_size': [100],
   'learning_rate': [0.1, 0.15, 0.2],
   'lambda_reg': [0, 0.001, 0.002, 0.004],
   'num_hidden': [50, 100, 150],
   'n_epochs': 400,
   'validate_params': ["batch_size", "learning_rate", "lambda_reg", 'num_hidden']}

# hyperparams = {
#     'batch_size': [100],
#     'learning_rate': [0.005],
#     'lambda_reg': [0.05],
#     'num_hidden': [40],
#     'n_epochs': 100,
#     'validate_params': ["batch_size", "learning_rate", "lambda_reg", 'num_hidden']}

# Cross-validate here
best_params, all_params = validation_helpers.validate_grid_search(train_fn, test_fn,
                                                                  False, train_samples, train_labels, valid_samples,
                                                                  valid_labels, hyperparams, num_repeat=2)

# Average results due to non-deterministic nature of the model
f1s = numpy.zeros((1, train_labels.shape[1]))
precisions = numpy.zeros((1, train_labels.shape[1]))
recalls = numpy.zeros((1, train_labels.shape[1]))

num_repeat = 3

print 'All params', all_params
print 'Best params', best_params

for i in range(num_repeat):
    model = train_fn(train_labels, train_samples, best_params)
    _, _, _, _, f1_c, precision_c, recall_c = test_fn(valid_labels, valid_samples, model)
    f1s += f1_c
    precisions += precision_c
    recalls += recall_c

f1s /= num_repeat
precisions /= num_repeat
recalls /= num_repeat

for i in range(len(all_aus)):
    print 'AU%d done: precision %.4f, recall %.4f, f1 %.4f\n' % (all_aus[i], precisions[0, i], recalls[0, i], f1s[0, i])
    f.write("%d %.4f %.4f %.4f\n" % (all_aus[i], precisions[0, i], recalls[0, i], f1s[0, i]))

f.close()
