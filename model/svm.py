import json
import os
import pathlib
import pickle
import time
from multiprocessing import Manager, Pool
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    balanced_accuracy_score,
    precision_score,
    plot_roc_curve,
    auc,
    roc_curve,
    precision_recall_curve,
    classification_report,
)
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import (
    RepeatedStratifiedKFold,
    RepeatedKFold,
    LeaveOneOut, GridSearchCV)
from sklearn.svm import SVC

from eval_regularisation import regularisation_heatmap
from utils._custom_split import LeaveNOut, BootstrapCustom_
from utils.visualisation import (
    plot_roc_range,
    build_proba_hist,
    build_individual_animal_pred,
    build_report,
    plot_ml_report_final,
    plot_high_dimension_db, plot_learning_curves, plot_fold_details, mean_confidence_interval, plot_ml_report_final_abs)

from sklearn.neighbors import KNeighborsClassifier
from sklearn import tree
from sklearn.linear_model import LogisticRegression

from var import parameters

from matplotlib import rcParams
# Set matplotlib to use Times New Roman
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']



def downsample_df(data_frame, class_healthy, class_unhealthy):
    df_true = data_frame[data_frame["target"] == class_unhealthy]
    df_false = data_frame[data_frame["target"] == class_healthy]
    try:
        if df_false.shape[0] > df_true.shape[0]:
            df_false = df_false.sample(df_true.shape[0])
        else:
            print("more 12 to 11.")
            df_true = df_true.sample(df_false.shape[0])
    except ValueError as e:
        print(e)
        return
    data_frame = pd.concat([df_true, df_false], ignore_index=True, sort=False)
    return data_frame


# def make_roc_curve(
#     class_healthy,
#     class_unhealthy,
#     clf_name,
#     out_dir,
#     classifier,
#     X,
#     y,
#     cv,
#     steps,
#     cv_name,
#     animal_ids,
#     days,
#     split1=None,
#     split2=None,
#     tag="",
# ):
#     steps = clf_name + "_" + steps
#     print("make_roc_curve %s" % cv_name, steps)
#     if isinstance(X, pd.DataFrame):
#         X = X.values
#
#     if isinstance(cv, LeaveOneOut):
#         roc_auc = loo_roc(
#             classifier, X, y, out_dir, cv_name, steps, animal_ids, cv, days
#         )
#         return roc_auc
#     else:
#         y_ground_truth_pr = []
#         y_proba_pr = []
#         tprs = []
#         aucs_roc = []
#         aucs_pr = []
#         precisions = []
#         recalls = []
#         mean_fpr = np.linspace(0, 1, 100)
#         plt.clf()
#         fig_roc, ax_roc = plt.subplots(figsize=(8.00, 6.00))
#         fig_pr, ax_pr = plt.subplots(figsize=(8.00, 6.00))
#         y_binary = (y.copy() != 1).astype(int)
#
#         data0 = []
#         data1 = []
#
#         if cv is None:
#             if split1 is None:
#                 a = [
#                     (np.arange(0, int(y.size / 2)), np.arange(int(y.size / 2), y.size))
#                 ]  # split in half
#             else:
#                 a = [(np.arange(0, split1), np.arange(split1, y.size))]
#         else:
#             a = cv.split(X, y)
#
#         for i, (train, test) in enumerate(a):
#             classifier.fit(X[train], y[train])
#             y_proba_test = classifier.predict_proba(X[test])[:, 1]
#             y_bin_test = y_binary[test]
#             h_0 = y_proba_test[y_bin_test == 0]
#             h_1 = y_proba_test[y_bin_test == 1]
#             data0.extend(h_0)
#             data1.extend(h_1)
#             if isinstance(cv, StratifiedLeaveTwoOut):
#                 print("make_roc_curve fold %d/%d" % (i, cv.nfold))
#                 viz_roc = plot_roc_curve(classifier, X[test], y[test])
#                 # viz_pr = plot_precision_recall_curve(classifier, X[test], y_binary[test])
#
#                 label = "%d auc=%d idx=%d" % (
#                     int(float(np.unique(cv.animal_ids[test])[0])),
#                     viz_roc.roc_auc * 100,
#                     test[0],
#                 )
#                 if viz_roc.roc_auc > 0.95:
#                     viz_roc = plot_roc_curve(
#                         classifier,
#                         X[test],
#                         y[test],
#                         label=label,
#                         alpha=1,
#                         lw=1.5,
#                         ax=ax_roc,
#                     )
#                     precision, recall, _ = precision_recall_curve(
#                         y_bin_test, y_proba_test
#                     )
#                     ax_pr.step(recall, precision, label=label, lw=1.5)
#                 elif viz_roc.roc_auc < 0.2:
#                     viz_roc = plot_roc_curve(
#                         classifier,
#                         X[test],
#                         y[test],
#                         label=label,
#                         alpha=1,
#                         lw=1.5,
#                         ax=ax_roc,
#                     )
#                     precision, recall, _ = precision_recall_curve(
#                         y_bin_test, y_proba_test
#                     )
#                     ax_pr.step(recall, precision, label=label, lw=1.5)
#                 else:
#                     viz_roc = plot_roc_curve(
#                         classifier,
#                         X[test],
#                         y[test],
#                         label=None,
#                         alpha=0.3,
#                         lw=1,
#                         ax=ax_roc,
#                         c="tab:blue",
#                     )
#                     precision, recall, _ = precision_recall_curve(
#                         y_bin_test, y_proba_test
#                     )
#                     ax_pr.step(recall, precision, label=None)
#             else:
#                 if cv is not None:
#                     print(
#                         "make_roc_curve fold %d/%d"
#                         % (i, cv.n_repeats * cv.cvargs["n_splits"])
#                     )
#                 else:
#                     print(f"make_roc_curve split={i}")
#
#                 if animal_ids is not None:
#                     animal_ids = np.array(animal_ids)
#                     print(
#                         "FOLD %d --> \nSAMPLE TRAIN IDX:" % i,
#                         train,
#                         "\nSAMPLE TEST IDX:",
#                         test,
#                         "\nTEST TARGET:",
#                         np.unique(y[test]),
#                         "\nTRAIN TARGET:",
#                         np.unique(y[train]),
#                         "\nTEST ANIMAL ID:",
#                         np.unique(animal_ids[test]),
#                         "\nTRAIN ANIMAL ID:",
#                         np.unique(animal_ids[train]),
#                     )
#
#                 viz_roc = plot_roc_curve(
#                     classifier,
#                     X[test],
#                     y[test],
#                     label=None,
#                     alpha=0.3,
#                     lw=1,
#                     ax=ax_roc,
#                     c="tab:blue",
#                 )
#                 precision, recall, _ = precision_recall_curve(y_bin_test, y_proba_test)
#                 y_pred = classifier.predict(X[test])
#                 ax_pr.step(recall, precision, label=None, lw=1, c="tab:blue")
#
#             interp_tpr = np.interp(mean_fpr, viz_roc.fpr, viz_roc.tpr)
#             interp_tpr[0] = 0.0
#             print("auc=", viz_roc.roc_auc)
#             if "TSNE(2)" in steps or "UMAP" in steps:
#                 plot_2d_decision_boundaries(
#                     viz_roc.roc_auc,
#                     i,
#                     X,
#                     y,
#                     X[test],
#                     y[test],
#                     X[train],
#                     y[train],
#                     steps,
#                     classifier,
#                     out_dir,
#                     steps,
#                     dimensionality_reduction="TSNE",
#                 )
#             if "PCA(3)" in steps and "linear" in steps.lower():
#                 plot_3D_decision_boundaries(
#                     X,
#                     y,
#                     X[train],
#                     y[train],
#                     X[test],
#                     y[test],
#                     steps,
#                     classifier,
#                     i,
#                     out_dir,
#                     steps,
#                     viz_roc.roc_auc,
#                 )
#             if "TSNE(3)" in steps and "linear" in steps.lower():
#                 plot_3D_decision_boundaries(
#                     X,
#                     y,
#                     X[train],
#                     y[train],
#                     X[test],
#                     y[test],
#                     steps,
#                     classifier,
#                     i,
#                     out_dir,
#                     steps,
#                     viz_roc.roc_auc,
#                     DR="TSNE",
#                 )
#
#             if np.isnan(viz_roc.roc_auc):
#                 continue
#             tprs.append(interp_tpr)
#             aucs_roc.append(viz_roc.roc_auc)
#             aucs_pr.append(auc(recall, precision))
#             precisions.append(precision)
#             info = f"train shape:{str(train.shape)} healthy:{np.sum(y[train] == class_healthy)} unhealthy:{np.sum(y[train] == class_unhealthy)}| test shape:{str(test.shape)} healthy:{np.sum(y[test] == class_healthy)} unhealthy:{np.sum(y[test] == class_unhealthy)}"
#             recalls.append(recall)
#
#             y_ground_truth_pr.append(y_binary[test])
#             y_proba_pr.append(classifier.predict_proba(X[test])[:, 1])
#
#             # ax.plot(viz.fpr, viz.tpr, c="tab:green")
#
#         print("make_roc_curve done!")
#         mean_auc = plot_roc_range(
#             ax_roc,
#             tprs,
#             mean_fpr,
#             aucs_roc,
#             out_dir,
#             steps,
#             fig_roc,
#             cv_name,
#             days,
#             info=info,
#             tag=tag,
#         )
#         mean_auc_pr = plot_pr_range(
#             ax_pr,
#             y_ground_truth_pr,
#             y_proba_pr,
#             aucs_pr,
#             out_dir,
#             steps,
#             fig_pr,
#             cv_name,
#             days,
#         )
#
#         plt.close(fig_roc)
#         plt.close(fig_pr)
#         plt.clf()
#         make_y_hist(data0, data1, out_dir, cv_name, steps, mean_auc, info=info, tag=tag)
#         return mean_auc, aucs_roc


def process_ml(
    classifiers,
    add_feature,
    meta_data,
    meta_data_short,
    output_dir,
    animal_ids,
    sample_dates,
    data_frame,
    activity_days,
    n_imputed_days,
    study_id,
    steps,
    n_splits,
    n_repeats,
    sampling,
    downsample_false_class,
    label_series,
    class_healthy_label,
    class_unhealthy_label,
    meta_columns,
    season,
    y_col="target",
    cv=None,
    save_model=False,
    augment_training=0,
    n_job=6,
    epoch=30,
    batch_size=8,
    time_freq_shape=None,
    individual_to_test=None,
    plot_2d_space=True,
    export_fig_as_pdf=True,
    wheather_days=None,
    syhth_thresh=2,
    C=None,
    gamma=None,
    enable_regularisation=False
):
    print("*******************************************************************")
    mlp_layers = (1000, 500, 100, 45, 30, 15)
    print(label_series)
    data_frame["id"] = animal_ids
    if downsample_false_class:
        data_frame = downsample_df(data_frame, 0, 1)

    #print("drop duplicates...")
    #data_frame = data_frame.drop_duplicates()
    # animal_ids = data_frame["id"].tolist()
    sample_idxs = data_frame.index.tolist()
    if cv == "StratifiedLeaveTwoOut":
        cross_validation_method = LeaveNOut(
            animal_ids, sample_idxs, stratified=True, verbose=True, max_comb=-1
        )

    if cv == "LeaveTwoOut":
        cross_validation_method = LeaveNOut(
            animal_ids, sample_idxs, stratified=False, verbose=True, max_comb=-1, leaven=2
        )

    if cv == "StratifiedLeaveOneOut":
        cross_validation_method = LeaveNOut(
            animal_ids, sample_idxs, stratified=True, verbose=True, max_comb=-1, leaven=1
        )

    if cv == "LeaveOneOut":
        if len(individual_to_test) > 0:
            cross_validation_method = LeaveNOut(
                animal_ids, sample_idxs, stratified=False, verbose=True, leaven=1, individual_to_test=individual_to_test
            )
        else:
            cross_validation_method = LeaveNOut(
                animal_ids, sample_idxs, stratified=False, verbose=True, max_comb=-1, leaven=1
            )

    if cv == "RepeatedStratifiedKFold":
        cross_validation_method = RepeatedStratifiedKFold(
            n_splits=n_splits, n_repeats=n_repeats, random_state=0
        )

    if cv == "RepeatedKFold":
        cross_validation_method = RepeatedKFold(
            n_splits=n_splits, n_repeats=n_repeats, random_state=0
        )

    if cv == "RepeatedKFoldMRNN":
        #todo fix
        from utils._custom_split import RepeatedKFoldCustom

        cross_validation_method = RepeatedKFoldCustom(
            2,
            2,
            metadata=None,
            days=activity_days,
            farmname="delmas",
            method="MRNN",
            out_dir=output_dir,
            N_META=len(meta_columns),
            full_activity_data_file=Path(
                "C:/Users/fo18103/PycharmProjects/PredictionOfHelminthsInfection/Data/delmas_activity_data_weather.csv"
            ),
        )

    if cv == "Bootstrap":
        cross_validation_method = BootstrapCustom_(animal_ids, n_iterations=len(animal_ids) * 10,
                                                   verbose=False)

    # if cv == "LeaveOneOut":
    #     cross_validation_method = LeaveOneOut()

    ids = data_frame["id"].values
    y_h = data_frame["health"].values.flatten()
    y_h = y_h.astype(int)
    y = data_frame[y_col].values.flatten()
    y = y.astype(int)

    # remove meta columns
    print("creating X...")
    X = data_frame.iloc[:, np.array([str(x).isnumeric() or x in add_feature for x in data_frame.columns])]
    X.columns = list(range(X.shape[1]))
    X = X.values

    print("release data_frame memory...")
    del data_frame
    print("****************************")

    if not os.path.exists(output_dir):
        print("mkdir", output_dir)
        os.makedirs(output_dir)

    print("************************************************")
    print("downsample on= " + str(downsample_false_class))
    class0_count = str(y_h[y_h == 0].size)
    class1_count = str(y_h[y_h == 1].size)
    print("X-> class0=" + class0_count + " class1=" + class1_count)

    if classifiers[0] in ["linear", "rbf", "dtree", "lreg", "knn"]:#todo reformat
        scores, scores_proba = cross_validate_svm_fast(
            save_model,
            classifiers,
            output_dir,
            steps,
            cv,
            activity_days,
            label_series,
            cross_validation_method,
            X,
            y,
            y_h,
            ids,
            meta_data,
            meta_columns,
            meta_data_short,
            sample_dates,
            augment_training,
            n_job,
            plot_2d_space,
            export_fig_as_pdf,
            syhth_thresh,
            C=C,
            gamma=gamma,
            enable_regularisation=enable_regularisation
        )

    # scores, scores_proba = cross_validate_custom(
    #     output_dir,
    #     steps,
    #     cv,
    #     activity_days,
    #     label_series,
    #     cross_validation_method,
    #     X,
    #     y,
    #     y_h,
    #     ids,
    #     sample_dates,
    # )

    if cv != "LeaveOneOut":
        build_individual_animal_pred(
            output_dir, steps, class_unhealthy_label, scores, ids, meta_columns
        )
        build_individual_animal_pred(
            output_dir, steps, class_unhealthy_label, scores, ids, meta_columns, tt="train"
        )
        build_proba_hist(output_dir, steps, class_unhealthy_label, scores_proba)

    build_report(
        output_dir,
        n_imputed_days,
        activity_days,
        wheather_days,
        scores,
        y_h,
        steps,
        study_id,
        sampling,
        season,
        downsample_false_class,
        activity_days,
        cv,
        cross_validation_method,
        class_healthy_label,
        class_unhealthy_label,
    )
    plot_ml_report_final(output_dir.parent.parent)
    try:
        plot_ml_report_final_abs(output_dir.parent.parent)
    except Exception as e:
        print(e)


def fold_worker(
    info,
    cv_name,
    save_model,
    out_dir,
    y_h,
    ids,
    meta,
    meta_data_short,
    sample_dates,
    days,
    steps,
    tprs_test,
    tprs_train,
    aucs_roc_test,
    aucs_roc_train,
    fold_results,
    fold_probas,
    label_series,
    mean_fpr_test,
    mean_fpr_train,
    clf,
    X,
    y,
    train_index,
    test_index,
    axis_test,
    axis_train,
    ifold,
    nfold,
    export_fig_as_pdf,
    plot_2d_space,
    clf_kernel,
    c,
    gamma
):
    print(f"process id={ifold}/{nfold}...")
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    y_h_train, y_h_test = y_h[train_index], y_h[test_index]
    ids_train, ids_test = ids[train_index], ids[test_index]

    meta_train, meta_test = meta[train_index], meta[test_index]
    meta_train_s, meta_test_s = (
        meta_data_short[train_index],
        meta_data_short[test_index],
    )

    sample_dates_train, sample_dates_test = (
        sample_dates[train_index],
        sample_dates[test_index],
    )
    class_healthy, class_unhealthy = 0, 1

    # hold all extra label
    fold_index = np.array(train_index.tolist() + test_index.tolist())
    X_fold = X[fold_index]
    y_fold = y[fold_index]
    ids_fold = ids[fold_index]
    sample_dates_fold = sample_dates[fold_index]
    meta_fold = meta[fold_index]

    # keep healthy and unhealthy only
    X_train = X_train[np.isin(y_h_train, [class_healthy, class_unhealthy])]
    y_train = y_h_train[np.isin(y_h_train, [class_healthy, class_unhealthy])]
    meta_train = meta_train[np.isin(y_h_train, [class_healthy, class_unhealthy])]
    meta_train_s = meta_train_s[np.isin(y_h_train, [class_healthy, class_unhealthy])]

    X_test = X_test[np.isin(y_h_test, [class_healthy, class_unhealthy])]
    y_test = y_h_test[np.isin(y_h_test, [class_healthy, class_unhealthy])]

    meta_test = meta_test[np.isin(y_h_test, [class_healthy, class_unhealthy])]
    meta_test_s = meta_test_s[np.isin(y_h_test, [class_healthy, class_unhealthy])]
    ids_test = ids_test[np.isin(y_h_test, [class_healthy, class_unhealthy])]
    sample_dates_test = sample_dates_test[
        np.isin(y_h_test, [class_healthy, class_unhealthy])
    ]

    ids_train = ids_train[np.isin(y_h_train, [class_healthy, class_unhealthy])]
    sample_dates_train = sample_dates_train[
        np.isin(y_h_train, [class_healthy, class_unhealthy])
    ]

    start_time = time.time()

    clf.fit(X_train, y_train)

    models_dir = out_dir / "models" / f"{type(clf).__name__}_{clf_kernel}_{steps}"
    models_dir.mkdir(parents=True, exist_ok=True)

    if hasattr(clf, "cv_results_"):
        df = pd.DataFrame(clf.cv_results_)
        filename = models_dir / f"regularisation_{ifold}.csv"
        df.to_csv(filename, index=False)

    fit_time = time.time() - start_time

    if save_model:
        models_dir = (
            out_dir / "models" / f"{type(clf).__name__}_{clf_kernel}_{days}_{steps}"
        )
        models_dir.mkdir(parents=True, exist_ok=True)
        filename = models_dir / f"model_{ifold}.pkl"
        print("saving classifier...")
        print(filename)
        with open(str(filename), "wb") as f:
            pickle.dump(clf, f)

    # test healthy/unhealthy
    y_pred_test = clf.predict(X_test)
    if hasattr(clf, 'decision_function'):
        y_pred_proba_test_df = clf.decision_function(X_test)
        y_pred_proba_test = clf.predict_proba(X_test)[:, 1]
    else:
        y_pred_proba_test = clf.predict_proba(X_test)[:, 1]
        y_pred_proba_test_df = y_pred_proba_test

    # prep for roc curve
    alpha = 0.3
    lw= 1
    # if len(y_test) < 150:
    #     alpha = len(y_test) / 100 / 4
    #     lw = len(y_test) / 100 / 4
    viz_roc_test = plot_roc_curve(
        clf,
        X_test,
        y_test,
        label=None,
        alpha=alpha,
        lw=lw,
        ax=None,
        c="tab:blue"
    )
    axis_test.append(viz_roc_test)

    interp_tpr_test = np.interp(mean_fpr_test, viz_roc_test.fpr, viz_roc_test.tpr)
    interp_tpr_test[0] = 0.0
    tprs_test.append(interp_tpr_test)
    auc_value_test = viz_roc_test.roc_auc
    print("auc test=", auc_value_test)

    if hasattr(clf, "best_estimator_"):
        print("gamma=", clf.best_estimator_._gamma)
        print("C=", clf.best_estimator_.C)

    aucs_roc_test.append(auc_value_test)

    viz_roc_train = plot_roc_curve(
        clf,
        X_train,
        y_train,
        label=None,
        alpha=0.3,
        lw=1,
        ax=None,
        c="tab:blue",
    )
    axis_train.append(viz_roc_train)

    interp_tpr_train = np.interp(mean_fpr_train, viz_roc_train.fpr, viz_roc_train.tpr)
    interp_tpr_train[0] = 0.0
    tprs_train.append(interp_tpr_train)
    auc_value_train = viz_roc_train.roc_auc
    print("auc train=", auc_value_train)
    aucs_roc_train.append(auc_value_train)

    if plot_2d_space and ifold <= 2:
        model = clf
        if hasattr(clf, "best_estimator_"):
            model = clf.best_estimator_

        print("2d testing...")
        plot_high_dimension_db(
            out_dir / "testing" / str(ifold),
            np.concatenate((X_train, X_test), axis=0),
            np.concatenate((y_train, y_test), axis=0),
            list(np.arange(len(X_train))),
            np.concatenate((meta_train, meta_test), axis=0),
            model,
            days,
            steps,
            ifold,
            export_fig_as_pdf,
        )
        # plot_learning_curves(model, X, y, ifold, out_dir / "testing" / str(ifold))

    accuracy = balanced_accuracy_score(y_test, y_pred_test)
    precision, recall, fscore, support = precision_recall_fscore_support(y_test, y_pred_test)
    if len(precision) == 1:
        precision = np.append(precision, precision[0])
        recall = np.append(recall, recall[0])
        fscore = np.append(fscore, fscore[0])
        support = np.append(support, support[0])

    correct_predictions_test = (y_test == y_pred_test).astype(int)
    incorrect_predictions_test = (y_test != y_pred_test).astype(int)

    # data for training
    y_pred_train = clf.predict(X_train)
    if hasattr(clf, 'decision_function'):
        y_pred_proba_train_df = clf.decision_function(X_train)
        y_pred_proba_train = clf.predict_proba(X_train)[:, 1]
    else:
        y_pred_proba_train = clf.predict_proba(X_train)[:, 1]
        y_pred_proba_train_df = y_pred_proba_train

    accuracy_train = balanced_accuracy_score(y_train, y_pred_train)
    (
        precision_train,
        recall_train,
        fscore_train,
        support_train,
    ) = precision_recall_fscore_support(y_train, y_pred_train)
    correct_predictions_train = (y_train == y_pred_train).astype(int)
    incorrect_predictions_train = (y_train != y_pred_train).astype(int)

    n_healthy = np.sum(y_test == int(class_healthy)) + np.sum(y_train == int(class_healthy))
    n_unhealthy = np.sum(y_test == int(class_unhealthy)) + np.sum(y_train == int(class_unhealthy))

    if hasattr(clf, "best_estimator_"):
        clf_kernel = clf.best_estimator_.kernel

    clf_name = type(clf).__name__
    if hasattr(clf, "best_estimator_"):
        clf_name = type(clf.best_estimator_).__name__

    fold_result = {
        "clf": clf_name,
        "days": days,
        "clf_kernel": clf_kernel,
        "cross_validation": cv_name,
        "steps": steps,
        "i_fold": ifold,
        "info": info,
        "training_shape": X_train.shape,
        "testing_shape": X_test.shape,
        "target": int(y_test.tolist()[0]),
        "auc": auc_value_test,
        "auc_train": auc_value_train,
        "accuracy": float(accuracy),
        "accuracy_train": float(accuracy_train),
        "class_healthy": int(class_healthy),
        "n_healthy": int(n_healthy),
        "n_unhealthy": int(n_unhealthy),
        "class_unhealthy": int(class_unhealthy),
        "y_test": y_test.tolist(),
        "y_train": y_train.tolist(),
        "y_pred_test": y_pred_test.tolist(),
        "y_pred_train": y_pred_train.tolist(),
        "y_pred_proba_test": y_pred_proba_test.tolist(),
        "y_pred_proba_train": y_pred_proba_train.tolist(),
        "y_pred_proba_test_df": y_pred_proba_test_df.tolist(),
        "y_pred_proba_train_df": y_pred_proba_train_df.tolist(),
        "ids_test": ids_test.tolist(),
        "ids_train": ids_train.tolist(),
        "sample_dates_test": sample_dates_test.tolist(),
        "sample_dates_train": sample_dates_train.tolist(),
        "meta_test": meta_test.tolist(),
        "meta_fold": meta_fold.tolist(),
        "meta_train": meta_train.tolist(),
        "correct_predictions_test": correct_predictions_test.tolist(),
        "incorrect_predictions_test": incorrect_predictions_test.tolist(),
        "correct_predictions_train": correct_predictions_train.tolist(),
        "incorrect_predictions_train": incorrect_predictions_train.tolist(),
        "test_precision_score_0": float(precision[0]),
        "test_precision_score_1": float(precision[1]),
        "test_recall_0": float(recall[0]),
        "test_recall_1": float(recall[1]),
        "test_fscore_0": float(fscore[0]),
        "test_fscore_1": float(fscore[1]),
        "test_support_0": float(support[0]),
        "test_support_1": float(support[1]),
        "train_precision_score_0": float(precision_train[0]),
        "train_precision_score_1": float(precision_train[1]),
        "train_recall_0": float(recall_train[0]),
        "train_recall_1": float(recall_train[1]),
        "train_fscore_0": float(fscore_train[0]),
        "train_fscore_1": float(fscore_train[1]),
        "train_support_0": float(support_train[0]),
        "train_support_1": float(support_train[1]),
        "fit_time": fit_time,
        "c": c,
        "gamma": gamma
    }
    print("export result to json...")
    out = out_dir / "fold_data"
    filepath = out / f"{ifold}_result.json"
    out.mkdir(parents=True, exist_ok=True)
    print(filepath)
    with open(str(filepath), "w") as fp:
        json.dump(fold_result, fp)
    fold_results.append(fold_result)

    # test individual labels and store probabilities to be healthy/unhealthy
    print(f"process id={ifold}/{nfold} test individual labels...")
    for y_f in np.unique(y_fold):
        label = label_series[y_f]
        X_test = X_fold[y_fold == y_f]
        y_test = y_fold[y_fold == y_f]
        if hasattr(clf, 'decision_function'):
            y_pred_proba_test = clf.decision_function(X_test)
        else:
            y_pred_proba_test = clf.predict_proba(X_test)[:, 1]
        # if len(np.array(y_pred_proba_test).shape) > 1:
        #     test_y_pred_proba_0 = y_pred_proba_test[:, 0]
        #     test_y_pred_proba_1 = y_pred_proba_test[:, 1]
        #     fold_proba = {
        #         "test_y_pred_proba_0": test_y_pred_proba_0.tolist(),
        #         "test_y_pred_proba_1": test_y_pred_proba_1.tolist(),
        #     }
        # else:
        fold_proba = {
            "test_y_pred_proba_0": y_pred_proba_test.tolist(),
            "test_y_pred_proba_1": y_pred_proba_test.tolist(),
        }
        fold_probas[label].append(fold_proba)
    print(f"process id={ifold}/{nfold} done!")


def find_test_samples_with_full_synthetic(meta_columns, meta, meta_test, test_index, n_i=2):
    if 'imputed_days' not in meta_columns:
        return test_index
    else:
        idx_i = meta_columns.index('imputed_days')
        new_test_index = test_index[meta_test[:, idx_i] < n_i]
        #meta[new_test_index] metadata of new testing samples without imputed days in them
        return new_test_index


def cross_validate_svm_fast(
    save_model,
    svc_kernel,
    out_dir,
    steps,
    cv_name,
    days,
    label_series,
    cross_validation_method,
    X,
    y,
    y_h,
    ids,
    meta,
    meta_columns,
    meta_data_short,
    sample_dates,
    augment_training,
    n_job=None,
    plot_2d_space=True,
    export_fig_as_pdf=True,
    syhth_thresh=2,
    C=None,
    gamma=None,
    enable_regularisation=False
):
    """Cross validate X,y data and plot roc curve with range
    Args:
        out_dir: output directory to save figures to
        steps: postprocessing steps
        cv_name: name of cross validation method
        days: count of activity days in sample
        label_series: dict that holds famacha label/target
        class_healthy: target integer of healthy class
        class_unhealthy: target integer of unhealthy class
        cross_validation_method: Cv object
        X: samples
        y: targets
    """
    # if plot_2d_space:
    #     for kernel in svc_kernel:
    #         try:
    #             if C is None or gamma is None:
    #                 clf = SVC(kernel=kernel, probability=True)
    #             else:
    #                 clf = SVC(kernel=kernel, probability=True, C=C, gamma=gamma)
    #             X_ = X[np.isin(y_h, [0, 1])]
    #             y_ = y_h[np.isin(y_h, [0, 1])]
    #             meta_ = meta_data_short[np.isin(y_h, [0, 1])]
    #             clf.fit(X_, y_)
    #             plot_high_dimension_db(
    #                 out_dir / "training",
    #                 X_,
    #                 y_,
    #                 None,
    #                 meta_,
    #                 clf,
    #                 days,
    #                 steps,
    #                 0,
    #                 export_fig_as_pdf
    #             )
    #             plot_learning_curves(clf, X_, y_, 0, out_dir / "training")
    #         except Exception as e:
    #             print(e)

    scores, scores_proba = {}, {}

    #tuned_parameters_rbf = { "gamma": [1e-10, 1], "C": [0.001, 0.1, 1]}
    #tuned_parameters_rbf = {'C': [0.1, 1, 10, 100], 'gamma': [1, 0.1, 0.01, 0.001]}

    # tuned_parameters_linear = [
    #     {"kernel": ["linear"], "C": [0.0000000001, 0.000001, 0.001, 0.1, 1, 10, 100, 1000]},
    # ]
    for kernel in svc_kernel:
        if kernel in ["linear", "rbf"]:
            if enable_regularisation:
                print("Grid search...")
                svc = SVC(probability=True)
                # parameters["kernel"] = [kernel]
                clf = GridSearchCV(svc, parameters, return_train_score=True, cv=5, scoring='roc_auc', n_jobs=-1)
            else:
                if C is not None and gamma is not None:
                    clf = SVC(kernel=kernel, probability=True, C=C, gamma=gamma)
                else:
                    clf = SVC(kernel=kernel, probability=True)
            #clf = GridSearchCV(clf, tuned_parameters_rbf, refit=True, verbose=3)


        if kernel in ["knn"]:
            n_neighbors = int(np.sqrt(len(y)))
            print(f"KNN K={n_neighbors}")
            clf = KNeighborsClassifier(n_jobs=-1, n_neighbors=n_neighbors)

        if kernel in ["dtree"]:
            clf = tree.DecisionTreeClassifier()

        if kernel in ["lreg"]:
            clf = LogisticRegression(n_jobs=-1)

        clf_kernel = kernel

        plt.clf()
        fig_roc, ax_roc = plt.subplots(1, 2)
        fig_roc_merge, ax_roc_merge = plt.subplots()
        mean_fpr_test = np.linspace(0, 1, 100)
        mean_fpr_train = np.linspace(0, 1, 100)

        with Manager() as manager:
            # create result holders
            tprs_test = manager.list()
            tprs_train = manager.list()
            axis_test = manager.list()
            axis_train = manager.list()
            aucs_roc_test = manager.list()
            aucs_roc_train = manager.list()
            fold_results = manager.list()
            fold_probas = manager.dict()
            for k in label_series.values():
                fold_probas[k] = manager.list()

            pool = Pool(processes=n_job)
            start = time.time()
            for ifold, (train_index, test_index) in enumerate(
                cross_validation_method.split(X, y)
            ):
                # idx_s = find_test_samples_with_full_synthetic(meta_columns, meta, meta[test_index], test_index, n_i=syhth_thresh)
                # test_index = idx_s
                info = {}
                pool.apply_async(
                    fold_worker,
                    (
                        info,
                        cv_name,
                        save_model,
                        out_dir,
                        y_h,
                        ids,
                        meta,
                        meta_data_short,
                        sample_dates,
                        days,
                        steps,
                        tprs_test,
                        tprs_train,
                        aucs_roc_test,
                        aucs_roc_train,
                        fold_results,
                        fold_probas,
                        label_series,
                        mean_fpr_test,
                        mean_fpr_train,
                        clf,
                        X,
                        y,
                        train_index,
                        test_index,
                        axis_test,
                        axis_train,
                        ifold,
                        cross_validation_method.get_n_splits(),
                        export_fig_as_pdf,
                        plot_2d_space,
                        clf_kernel,
                        C,
                        gamma
                    ),
                )
            pool.close()
            pool.join()
            end = time.time()
            fold_results = list(fold_results)
            axis_test = list(axis_test)
            tprs_test = list(tprs_test)
            aucs_roc_test = list(aucs_roc_test)
            axis_train = list(axis_train)
            tprs_train = list(tprs_train)
            aucs_roc_train = list(aucs_roc_train)
            fold_probas = dict(fold_probas)
            fold_probas = dict([a, list(x)] for a, x in fold_probas.items())
            print("total time (s)= " + str(end - start))

        plot_fold_details(fold_results, meta, meta_columns, out_dir)

        if enable_regularisation:
            models_dir = out_dir / "models" / f"{type(clf).__name__}_{clf_kernel}_{steps}"
            regularisation_heatmap(models_dir, out_dir / "regularisation")

        info = f"X shape:{str(X.shape)} healthy:{fold_results[0]['n_healthy']} unhealthy:{fold_results[0]['n_unhealthy']} \n" \
               f" training_shape:{fold_results[0]['training_shape']} testing_shape:{fold_results[0]['testing_shape']}"

        for n, a in enumerate(axis_test):
            f, ax = a.figure_, a.ax_
            xdata = ax.lines[0].get_xdata()
            ydata = ax.lines[0].get_ydata()
            alpha = 0.3
            lw = 1
            # testing_shape = fold_results[n]["testing_shape"][0]
            # if testing_shape < 150:
            #     alpha = testing_shape / 100 / 5
            #     lw = testing_shape / 100 / 5
            ax_roc[1].plot(xdata, ydata, color="tab:blue", alpha=alpha, linewidth=lw)
            ax_roc_merge.plot(xdata, ydata, color="tab:blue", alpha=lw, linewidth=lw)

        for idx, a in enumerate(axis_train):
            f, ax = a.figure_, a.ax_
            if len(ax.lines) == 0:
                continue
            xdata = ax.lines[0].get_xdata()
            ydata = ax.lines[0].get_ydata()
            ax_roc[0].plot(xdata, ydata, color="tab:blue", alpha=0.3, linewidth=1)
            ax_roc_merge.plot(xdata, ydata, color="tab:purple", alpha=0.3, linewidth=1)

        if cv_name == "Bootstrap":
            tprs_test, fpr_test = [], []
            tprs_train, fpr_train = [], []
            aucs_train, aucs_test = [], []
            for k in range(0, len(fold_results), len(ids)):
                start = k
                end = k + len(ids)
                print(start, end)
                all_y_test = []
                all_probs_test = []
                for item in fold_results[start: end]:
                    all_y_test.extend(item['y_test'])
                    y_pred_proba_test = np.array(item['y_pred_proba_test'])
                    all_probs_test.extend(y_pred_proba_test)
                all_y_test = np.array(all_y_test)
                all_probs_test = np.array(all_probs_test)
                fpr, tpr, thresholds = roc_curve(all_y_test, all_probs_test.astype(int))
                tprs_test.append(tpr)
                fpr_test.append(fpr)
                roc_auc_test = auc(fpr, tpr)
                aucs_test.append(roc_auc_test)
                print(f"LOO AUC TEST={roc_auc_test}")
                ax_roc_merge.plot(fpr, tpr, lw=2, alpha=0.5, color="tab:blue", label=None)

                all_y_train = []
                all_probs_train = []
                for item in fold_results[start: end]:
                    all_y_train.extend(item['y_train'])
                    y_pred_proba_train = np.array(item['y_pred_proba_train'])
                    # if len(y_pred_proba_train) > 1:
                    #     y_pred_proba_train = y_pred_proba_train[:, 1]
                    all_probs_train.extend(y_pred_proba_train)
                all_y_train = np.array(all_y_train)
                all_probs_train = np.array(all_probs_train)
                fpr, tpr, thresholds = roc_curve(all_y_train, all_probs_train)
                tprs_train.append(tpr)
                fpr_train.append(fpr)
                roc_auc_train = auc(fpr, tpr)
                aucs_train.append(roc_auc_train)
                print(f"LOO AUC TRAIN={roc_auc_train}")
                ax_roc_merge.plot(fpr, tpr, lw=2, alpha=0.5, color="tab:purple", label=None)
            #cli
            mean_tpr_test = np.mean(tprs_test, axis=0)
            mean_fpr_test = np.mean(fpr_test, axis=0)
            mean_tpr_test[-1] = 1.0
            #mean_auc_test = auc(mean_fpr_test, mean_tpr_test)
            # std_auc = np.std(aucs)
            lo, hi = mean_confidence_interval(aucs_test)

            # label = f"Median ROC Test (Median AUC = {np.median(aucs_test):.2f}, 95% CI [{lo:.4f}, {hi:.4f}] )"
            label = f"Testing Median AUC = {np.median(aucs_test)*100:.1f}({lo:.2f}, {hi:.2f})"
            # if len(aucs_test) <= 2:
            #     label = r"Mean ROC (Median AUC = %0.2f)" % np.median(aucs_test)
            ax_roc_merge.plot(mean_fpr_test, mean_tpr_test, label=label, lw=2, alpha=1, color="black")

            mean_tpr_train = np.mean(tprs_train, axis=0)
            mean_fpr_train = np.mean(fpr_train, axis=0)

            mean_tpr_train[-1] = 1.0
            #mean_auc_train = auc(mean_fpr_train, mean_tpr_train)
            # std_auc = np.std(aucs)
            lo, hi = mean_confidence_interval(aucs_train)

            #label = f"Median ROC Training (Median AUC = {np.median(aucs_train):.2f}, 95% CI [{lo:.4f}, {hi:.4f}] )"
            label = f"Training Median AUC = {np.median(aucs_train)*100:.1f}({lo:.2f}, {hi:.2f})"
            # if len(aucs_train) <= 2:
            #     label = r"Mean ROC (Median AUC = %0.2f)" % np.median(aucs_train)
            ax_roc_merge.plot(
                mean_fpr_train, mean_tpr_train, label=label, lw=2, alpha=1, color="red"
            )

            ax_roc_merge.plot([0, 1], [0, 1], linestyle='--', lw=2, color='orange', label='Chance', alpha=1)
            ax_roc_merge.set_xlim([-0.05, 1.05])
            ax_roc_merge.set_ylim([-0.05, 1.05])
            ax_roc_merge.set_xlabel('False Positive Rate', fontsize=22)
            ax_roc_merge.set_ylabel('True Positive Rate', fontsize=22)
            #ax_roc_merge.set_title('Receiver operating characteristic')
            ax_roc_merge.legend(loc="lower right", fontsize=14)
            ax_roc_merge.grid()
            fig_roc.tight_layout()
            path = out_dir / "roc_curve" / cv_name
            path.mkdir(parents=True, exist_ok=True)
            tag = f"{type(clf).__name__}_{clf_kernel}"
            final_path = path / f"{tag}_roc_{steps}.png"
            print(final_path)
            fig_roc.set_size_inches(6, 6)
            fig_roc.tight_layout()

            ax_roc_merge.tick_params(axis='x', labelsize=18)  # Adjust the fontsize as needed for the x-axis
            ax_roc_merge.tick_params(axis='y', labelsize=18)

            fig_roc.savefig(final_path, dpi=500)
            # fig_roc.savefig(final_path)

            final_path = path / f"{tag}_roc_{steps}_merge.png"
            print(final_path)

            fig_roc_merge.set_size_inches(4.4, 4.4)
            fig_roc_merge.tight_layout()
            fig_roc_merge.savefig(final_path, dpi=500)
            #fig_roc_merge.savefig(final_path)

            if export_fig_as_pdf:
                final_path = path / f"{tag}_roc_{steps}.pdf"
                print(final_path)
                fig_roc.savefig(final_path)

                final_path = path / f"{tag}_roc_{steps}_merge.pdf"
                print(final_path)
                fig_roc_merge.savefig(final_path)

        if cv_name == "LeaveOneOut":
            all_y_test = []
            all_probs_test = []
            for item in fold_results:
                all_y_test.extend(item['y_test'])
                y_pred_proba_test = np.array(item['y_pred_test'])
                # if len(y_pred_proba_test) > 1:
                #     y_pred_proba_test = y_pred_proba_test[:, 1]
                all_probs_test.extend(y_pred_proba_test)
            all_y_test = np.array(all_y_test)
            all_probs_test = np.array(all_probs_test)
            fpr, tpr, thresholds = roc_curve(all_y_test, all_probs_test.astype(int))
            roc_auc_test = auc(fpr, tpr)
            print(f"LOO AUC TEST={roc_auc_test}")
            ax_roc_merge.plot(fpr, tpr, lw=3, alpha=0.9, label='LOOCV ROC (TEST AUC = %0.2f)' % (roc_auc_test))

            all_y_train = []
            all_probs_train = []
            for item in fold_results:
                all_y_train.extend(item['y_train'])
                y_pred_proba_train = np.array(item['y_pred_proba_train'])
                # if len(y_pred_proba_train) > 1:
                #     y_pred_proba_train = y_pred_proba_train[:, 1]
                all_probs_train.extend(y_pred_proba_train)
            all_y_train = np.array(all_y_train)
            all_probs_train = np.array(all_probs_train)
            fpr, tpr, thresholds = roc_curve(all_y_train, all_probs_train)
            roc_auc_train = auc(fpr, tpr)
            print(f"LOO AUC TRAIN={roc_auc_train}")
            ax_roc_merge.plot(fpr, tpr, lw=2, alpha=0.5, label='LOOCV ROC (TRAIN AUC = %0.2f)' % (roc_auc_train))

            ax_roc_merge.plot([0, 1], [0, 1], linestyle='--', lw=2, color='k', label='Chance level', alpha=.8)
            ax_roc_merge.set_xlim([-0.05, 1.05])
            ax_roc_merge.set_ylim([-0.05, 1.05])
            ax_roc_merge.set_xlabel('False Positive Rate', fontsize=22)
            ax_roc_merge.set_ylabel('True Positive Rate', fontsize=22)
            #ax_roc_merge.set_title('Receiver operating characteristic')
            ax_roc_merge.legend(loc="lower right", fontsize=14)
            ax_roc_merge.grid()
            fig_roc.tight_layout()
            path = out_dir / "roc_curve" / cv_name
            path.mkdir(parents=True, exist_ok=True)
            tag = f"{type(clf).__name__}_{clf_kernel}"
            final_path = path / f"{tag}_roc_{steps}.png"
            print(final_path)
            # fig_roc.savefig(final_path)

            final_path = path / f"{tag}_roc_{steps}_merge.png"
            print(final_path)
            fig_roc_merge.savefig(final_path)

            if export_fig_as_pdf:
                final_path = path / f"{tag}_roc_{steps}.pdf"
                print(final_path)
                fig_roc.savefig(final_path)

                final_path = path / f"{tag}_roc_{steps}_merge.pdf"
                print(final_path)
                fig_roc_merge.savefig(final_path)

        if cv_name not in ["LeaveOneOut", "Bootstrap"]:
            mean_auc = plot_roc_range(
                ax_roc_merge,
                ax_roc,
                tprs_test,
                mean_fpr_test,
                aucs_roc_test,
                tprs_train,
                mean_fpr_train,
                aucs_roc_train,
                out_dir,
                steps,
                fig_roc,
                fig_roc_merge,
                cv_name,
                days,
                info=info,
                tag=f"{type(clf).__name__}_{clf_kernel}",
                export_fig_as_pdf=export_fig_as_pdf,
            )

        scores[f"{type(clf).__name__}_{clf_kernel}_results"] = fold_results
        scores_proba[f"{type(clf).__name__}_{clf_kernel}_probas"] = fold_probas

    print("export results to json...")
    filepath = out_dir / "results.json"
    print(filepath)
    with open(str(filepath), "w") as fp:
        json.dump(scores, fp)
    filepath = out_dir / "results_proba.json"
    print(filepath)
    with open(str(filepath), "w") as fp:
        json.dump(scores_proba, fp)

    return scores, scores_proba


def loo_roc(clf, X, y, out_dir, cv_name, classifier_name, animal_ids, cv, days):
    all_y = []
    all_probs = []
    i = 0
    y_binary = (y.copy() != 1).astype(int)
    n = cv.get_n_splits(X, y_binary)
    for train, test in cv.split(X, y_binary):
        animal_ids = np.array(animal_ids)
        print("make_roc_curve fold %d/%d" % (i, n))
        # print(
        #     "FOLD %d --> \nSAMPLE TRAIN IDX:" % i,
        #     train,
        #     "\nSAMPLE TEST IDX:",
        #     test,
        #     "\nTEST TARGET:",
        #     np.unique(y_binary[test]),
        #     "\nTRAIN TARGET:",
        #     np.unique(y_binary[train]),
        #     "\nTEST ANIMAL ID:",
        #     np.unique(animal_ids[test]),
        #     "\nTRAIN ANIMAL ID:",
        #     np.unique(animal_ids[train]),
        # )
        i += 1
        all_y.append(y_binary[test])

        y_predict_proba = clf.fit(X[train], y_binary[train]).predict_proba(X[test])[
            :, 1
        ]
        all_probs.append(y_predict_proba)

    all_y = np.array(all_y)
    all_probs = np.array(all_probs)

    fpr, tpr, thresholds = roc_curve(all_y, all_probs)
    roc_auc = auc(fpr, tpr)
    fig, ax = plt.subplots(figsize=(12.80, 7.20))
    ax.plot(fpr, tpr, lw=2, alpha=0.5, label="LOOCV ROC (AUC = %0.2f)" % (roc_auc))
    ax.plot(
        [0, 1], [0, 1], linestyle="--", lw=2, color="k", label="Chance level", alpha=0.8
    )
    ax.set_xlim([-0.05, 1.05])
    ax.set_ylim([-0.05, 1.05])
    ax.set_xlabel("False Positive Rate", fontsize=22)
    ax.set_ylabel("True Positive Rate", fontsize=22)
    ax.set_title(
        "Receiver operating characteristic LOOCV (at sample level) days=%d" % days
    )
    ax.legend(loc="lower right", fontsize=14)
    ax.grid()
    path = out_dir / "roc_curve" / cv_name
    final_path = path / f"roc_{classifier_name}.png"
    print(final_path)
    fig.savefig(final_path)
    plt.close(fig)
    plt.clf()

    precision, recall, thresholds = precision_recall_curve(all_y, all_probs)
    pr_auc = auc(recall, precision)
    fig, ax = plt.subplots(figsize=(12.80, 7.20))
    ax.plot(
        recall, precision, lw=2, alpha=0.5, label="LOOCV PR (AUC = %0.2f)" % (pr_auc)
    )
    # ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='k', label='Chance level', alpha=.8)
    ax.set_xlim([-0.05, 1.05])
    ax.set_ylim([-0.05, 1.05])
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision Recall LOOCV (at sample level)")
    ax.legend(loc="lower right", fontsize=14)
    ax.grid()
    path = out_dir / "pr_curve" / cv_name
    final_path = path / f"pr_{classifier_name}.png"
    print(final_path)
    fig.savefig(final_path)
    plt.close(fig)
    plt.clf()
    return roc_auc


def make_y_hist(data0, data1, out_dir, cv_name, steps, auc, info="", tag=""):
    plt.figure(figsize=(8, 6))
    plt.hist(data0, bins=100, alpha=0.5, label="healthy (y=0)")
    plt.hist(data1, bins=100, alpha=0.5, label="unhealthy (y=1)")
    plt.xlabel("Y probability", size=14)
    plt.ylabel("Count", size=14)
    plt.title(
        "Histograms of prediction probabilities (ROC Mean AUC = %0.2f)\n %s"
        % (auc, info)
    )
    plt.legend(loc="upper right", fontsize=14)
    filename = "%s/%s_overlapping_histograms_y_%s_%s.png" % (
        out_dir,
        tag,
        cv_name,
        steps,
    )
    print(filename)
    plt.savefig(filename)
    plt.clf()


def process_clf_(
    steps,
    X_test,
    y_test,
    model_path,
    output_dir
):
    """Test data with previously saved model
    Args:
    """
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

    plt.clf()
    fig_roc, ax_roc = plt.subplots(figsize=(19.20, 10.80))
    fig_roc_merge, ax_roc_merge = plt.subplots(figsize=(12.80, 7.20))
    mean_fpr = np.linspace(0, 1, 100)
    tprs = []
    aucs_roc = []

    models = list(model_path.glob('*.pkl'))
    for i, model_file in enumerate(models):
        with open(str(model_file), 'rb') as f:
            clf = pickle.load(f)
            y_pred = clf.predict(X_test.copy())
            print(classification_report(y_test, y_pred))
            print(f"precision_score: {precision_score(y_test, y_pred, average='weighted')}")

            pathlib.Path(output_dir / "reports").mkdir(parents=True, exist_ok=True)
            df = pd.DataFrame(classification_report(y_test, y_pred, output_dict=True))

            filename = f"{output_dir / 'reports'}/report_{i}.csv"
            print(filename)
            df.to_csv(filename)

            viz_roc = plot_roc_curve(
                clf,
                X_test,
                y_test,
                label=None,
                alpha=0.3,
                lw=1,
                ax=ax_roc,
                c="tab:blue",
            )
            interp_tpr = np.interp(mean_fpr, viz_roc.fpr, viz_roc.tpr)
            interp_tpr[0] = 0.0
            print("auc=", viz_roc.roc_auc)
            tprs.append(interp_tpr)
            aucs_roc.append(viz_roc.roc_auc)

    info = (
        f"X_test shape:{str(X_test.shape)} healthy:{np.sum(y_test == 0)} unhealthy:{np.sum(y_test == 1)}"
    )
    mean_auc = plot_roc_range(
        ax_roc,
        tprs,
        mean_fpr,
        aucs_roc,
        output_dir,
        steps,
        fig_roc,
        f"nfold={len(models)}",
        7,
        info=info,
        tag=f"{type(clf).__name__}",
    )


def process_clf(
    n_activity_days,
    train_size,
    label_series_f1,
    label_series_f2,
    info_,
    steps,
    n_fold,
    X_train,
    X_test,
    y_train,
    y_test,
    output_dir,
    n_job=None,
    export_fig_as_pdf=None,
    plot_2d_space=True
):
    """Trains multiple model with n 90% samples
    Args:
        label_series_f1: famacha/target dict for famr1
        label_series_f2: famacha/target dict for famr2
        info_: meta on healthy/unhealthy target
        steps: preprocessing steps
        n_fold: number of 90% chunks
        X_train: all samples in farm 1
        X_test: all samples in farm 2
        y_train: all targets in farm 1
        y_test: all targets in farm 2
        output_dir: figure output directory
    """
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    label_series_f1_r = {v: k for k, v in label_series_f1.items()}
    label_series_f2_r = {v: k for k, v in label_series_f2.items()}
    # prep the data
    mask = np.isin(y_train, [0, 1])
    X_train = X_train[mask]
    y_train = y_train[mask]

    mask = np.isin(y_test, [0, 1])
    X_test = X_test[mask]
    y_test = y_test[mask]

    # build 90% folds
    folds = []
    cpt_fold = 0
    while True:
        df = pd.DataFrame(X_train)
        df["target"] = y_train
        fold = df.sample(frac=train_size, random_state=cpt_fold)
        y = fold["target"].values
        fold = fold.drop("target", 1)
        X = fold.values
        if len(np.unique(y)) == 1:
            print("Only one class present in y_true. skip.")
            continue
        folds.append([X, y])
        # print(y)
        cpt_fold += 1
        if cpt_fold >= n_fold:
            print(f"found {n_fold} 90% folds.")
            break

    # results = []
    plt.clf()
    fig_roc, ax_roc = plt.subplots(1, 2)
    fig_roc_merge, ax_roc_merge = plt.subplots()
    mean_fpr_test = np.linspace(0, 1, 100)
    tprs_test = []
    aucs_roc_test = []

    mean_fpr_train = np.linspace(0, 1, 100)
    tprs_train = []
    aucs_roc_train = []
    for i, (X_train, y_train) in enumerate(folds):
        print(f"progress {i}/{n_fold} ...")
        #clf = SVC(kernel="rbf", probability=True)
        tuned_parameters = [
            {
                "kernel": ["rbf"],
                "gamma": ["scale", 1e-1, 1e-3, 1e-4],
                "class_weight": [None, "balanced"],
                "C": [0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000],
            },
            {"kernel": ["linear"], "C": [1, 10, 100, 1000]},
        ]

        clf = GridSearchCV(
            SVC(probability=True),
            tuned_parameters,
            scoring=["roc_auc", "accuracy", "precision"],
            refit="accuracy",
            n_jobs=-1,
        )
        clf.fit(X_train.copy(), y_train.copy())

        clf_best = clf
        print("Best estimator from gridsearch=")
        print(clf_best)
        y_pred_test = clf.predict(X_test.copy())
        y_pred_train = clf.predict(X_train.copy())
        print(classification_report(y_test, y_pred_test))
        print(f"precision_score: {precision_score(y_test, y_pred_test, average='weighted')}")

        pathlib.Path(output_dir / "reports").mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(classification_report(y_test, y_pred_test, output_dict=True))

        filename = f"{output_dir / 'reports'}/report_{i}.csv"
        print(filename)
        df.to_csv(filename)

        if plot_2d_space and i <= 2:
            model = clf
            if hasattr(clf, "best_estimator_"):
                model = clf.best_estimator_
            plot_high_dimension_db(
                output_dir / "testing",
                np.concatenate((X_train, X_test), axis=0),
                np.concatenate((y_train, y_test), axis=0),
                list(np.arange(len(X_train))),
                [],
                model,
                n_activity_days,
                steps,
                i,
                export_fig_as_pdf
            )

        # X = np.array(X_train.tolist() + X_test.tolist())
        # y = np.array(y_train.tolist() + y_test.tolist())
        # results.append([clf_best, X, y])

        # todo remove redundant
        auc_check = plot_roc_curve(
            clf,
            X_test,
            y_test,
            label=None,
            alpha=0,
            lw=1,
            ax=ax_roc[1],
            c="tab:blue",
        )

        if auc_check.roc_auc > 0.5:
            viz_roc_test = plot_roc_curve(
                clf,
                X_test,
                y_test,
                label=None,
                alpha=0.3,
                lw=1,
                ax=ax_roc[1],
                c="tab:blue",
            )
            _ = plot_roc_curve(
                clf,
                X_test,
                y_test,
                label=None,
                alpha=0.3,
                lw=1,
                ax=ax_roc_merge,
                c="tab:blue",
            )
        interp_tpr_test = np.interp(mean_fpr_test, viz_roc_test.fpr, viz_roc_test.tpr)
        interp_tpr_test[0] = 0.0
        print("auc=", viz_roc_test.roc_auc)
        tprs_test.append(interp_tpr_test)
        aucs_roc_test.append(viz_roc_test.roc_auc)

        viz_roc_train = plot_roc_curve(
            clf,
            X_train,
            y_train,
            label=None,
            alpha=0.3,
            lw=1,
            ax=ax_roc[0],
            c="tab:blue",
        )
        _ = plot_roc_curve(
            clf,
            X_train,
            y_train,
            label=None,
            alpha=0.3,
            lw=1,
            ax=ax_roc_merge,
            c="tab:purple",
        )
        interp_tpr_train = np.interp(mean_fpr_train, viz_roc_train.fpr, viz_roc_train.tpr)
        interp_tpr_train[0] = 0.0
        print("auc train=", viz_roc_train.roc_auc)
        tprs_train.append(interp_tpr_train)
        aucs_roc_train.append(viz_roc_train.roc_auc)

    info = (
        f"X_train shape:{str(X_train.shape)} healthy:{np.sum(y_train == 0)} unhealthy:{np.sum(y_train == 1)} \n "
        f"X_test shape:{str(X_test.shape)} healthy:{np.sum(y_test == 0)} unhealthy:{np.sum(y_test == 1)} \n {info_}"
    )
    mean_auc = plot_roc_range(
        ax_roc_merge,
        ax_roc,
        tprs_test,
        mean_fpr_test,
        aucs_roc_test,
        tprs_train,
        mean_fpr_train,
        aucs_roc_train,
        output_dir,
        steps,
        fig_roc,
        fig_roc_merge,
        f"90% fold {n_fold}",
        n_activity_days,
        info=info,
        tag=f"{type(clf).__name__}",
    )

    # return results
