import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt


def plot_heatmap(df, col, out_dir, title=""):
    df = df.fillna("linear")
    for g in df["gamma"].unique():
        df_ = df[df["gamma"] == g]
        scores = df_[col].values
        scores = np.array(scores).reshape(len(df_["C"].unique()), len(df_["gamma"].unique()))
        #plt.figure(figsize=(8, 6))
        #plt.subplots_adjust(left=.2, right=0.95, bottom=0.15, top=0.95)
        fig, ax = plt.subplots()
        im = ax.imshow(scores[::-1, :], interpolation='nearest')
        # im = ax.imshow(scores, interpolation='nearest',
        #            norm=MidpointNormalize(vmin=-.2, midpoint=0.5))
        # ax.set_xlabel('gamma')
        ax.set_ylabel('C')
        fig.colorbar(im)
        ax.set_xticks(np.arange(len(df_["gamma"].unique())), [i for i in df_["gamma"].unique()], rotation=45)
        ax.set_yticks(np.arange(len(df_["C"].unique()))[::-1],
                   [np.format_float_scientific(i, ) for i in df_["C"].unique()])
        ax.set_title(f'Regularisation AUC\n{title}')
        fig.tight_layout()
        fig.show()
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"heatmap_{g}_{col}_{title}.png".replace(":", "_").replace(" ", "_")
        filepath = out_dir / filename
        print(filepath)


def plot_fig(df, col, out_dir, title=""):
    scores = df[col].values
    scores = np.array(scores).reshape(len(df["C"].unique()), len(df["gamma"].unique()))
    Cs = df["C"].unique()
    Gammas = df["gamma"].unique()
    fig, ax = plt.subplots()
    for ind, i in enumerate(Cs):
        ax.plot(Gammas, scores[ind], label="C: " + str(i))
    ax.set_title(title)
    ax.set_xscale('log')
    ax.legend()
    ax.set_xlabel("Gamma")
    ax.set_ylabel("Accuracy")
    fig.tight_layout()
    fig.show()
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"plot_{col}_{title}.png".replace(":", "_").replace(" ", "_")
    filepath = out_dir / filename
    print(filepath)
    fig.savefig(filepath)


def regularisation_heatmap(data_dir, out_dir):
    files = list(data_dir.glob("*.csv"))
    print(data_dir)
    print(files)
    dfs = []
    mean_test_score_list = []
    mean_train_score_list = []
    for file in files:
        df = pd.read_csv(file)
        data = df[["param_gamma", "param_C", "mean_test_score", "mean_train_score"]]
        data = data.assign(fold=int(file.stem.split('_')[1]))
        data = data.sort_values(["param_gamma", "param_C"])
        mean_test_score_list.append(data["mean_test_score"].values)
        mean_train_score_list.append(data["mean_train_score"].values)
        dfs.append(data)
    df_data = pd.DataFrame()
    df_data["gamma"] = df["param_gamma"]
    df_data["C"] = df["param_C"]
    df_data["mean_test_score"] = pd.DataFrame(mean_test_score_list).mean()
    df_data["mean_train_score"] = pd.DataFrame(mean_train_score_list).mean()

    plot_heatmap(
        df_data,
        "mean_train_score",
        out_dir,
        f"GridSearch Training model:{data_dir.parent.parent.name}",
    )
    plot_heatmap(
        df_data,
        "mean_test_score",
        out_dir,
        f"GridSearch Testing model:{data_dir.parent.parent.name}",
    )

    # plot_fig(
    #     df_data,
    #     "mean_test_score",
    #     out_dir,
    #     f"GridSearch Testing model:{data_dir.parent.parent.name}",
    # )


if __name__ == "__main__":
    # scores = np.arange(0, 60)
    # df = pd.DataFrame()
    # C = np.arange(0, 4)
    # Gamma = np.arange(0, 15)
    #
    # scores = np.array(scores).reshape(len(C), len(Gamma))

    input_folder = Path("C:/Users/fo18103/PycharmProjects/pythonProject/PredictionOfDHealthInSR/output_debug_3/main_experiment/rbf/delmas_dataset4_mrnn_7day/delmas_dataset4_mrnn_7day_delmas_RepeatedKFold_7_7_QN_ANSCOMBE_LOG/2To2/models/GridSearchCV_rbf_QN_ANSCOMBE_LOG")
    out_dir = Path("C:/Users/fo18103/PycharmProjects/pythonProject/PredictionOfDHealthInSR/output_debug_3")
    regularisation_heatmap(input_folder, out_dir)