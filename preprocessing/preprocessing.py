import gc
import warnings
import pandas as pd
import numpy as np
#import umap
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler, MinMaxScaler, Normalizer

from cwt._cwt import STFT, CWT, CWTVisualisation, DWT

from utils._anscombe import Anscombe, Sqrt, Log
from utils._normalisation import CenterScaler, QuotientNormalizer
from utils.resampling import resample_s
from utils.visualisation import plot_distribution


def apply_preprocessing_steps(
    meta_columns,
    days,
    df_hum,
    df_temp,
    df_rainfall,
    df_windspeed,
    sfft_window,
    dwt_window,
    wavelet_f0,
    animal_ids,
    df,
    output_dir,
    steps,
    class_healthy_label,
    class_unhealthy_label,
    clf_name="",
    output_dim=2,
    n_scales=9,
    farm_name="",
    keep_meta=False,
    plot_all_target=None,
    enable_graph_out=None,
    output_qn_graph=False,
    sub_sample_scales=1,
):
    time_freq_shape = None
    N_META = len(meta_columns)
    step_slug = "_".join(steps)
    step_slug = farm_name + "_" + step_slug
    graph_outputdir = output_dir / "input_graphs"
    graph_outputdir.mkdir(parents=True, exist_ok=True)
    graph_outputdir = graph_outputdir / clf_name / step_slug

    # if len(steps) == 0:
    #     print("no steps to apply! return data as is")
    #     return df
    print("BEFORE STEP ->", df)
    # plotDistribution(df.iloc[:, :-N_META].values, graph_outputdir, "data_distribution_before_%s" % step_slug)
    for step in steps:
        # if step not in [
        #     "ANSCOMBE",
        #     "LOG",
        #     "QN",
        #     "CWT",
        #     "CENTER",
        #     "MINMAX",
        #     "PCA",
        #     "BASELINERM",
        #     "STFT",
        #     "STANDARDSCALER",
        #     "DIFFAPPEND",
        #     "DIFFLASTD",
        #     "DIFF",
        #     "DIFFLASTDAPPEND",
        #     "TSNE",
        # ]:
        #     warnings.warn("processing step %s does not exist!" % step)
        # plotDistribution(df.iloc[:, :-N_META].values, graph_outputdir, "data_distribution_before_%s" % step)
        print("applying STEP->%s in [%s]..." % (step, step_slug.replace("_", "->")))
        if step == "TEMPERATUREAPPEND":
            df_activity = df.copy().iloc[:, :-N_META]
            #df_activity.index = df.index  # need to keep original sample index!!!!
            df_meta = df.iloc[:, -N_META:]
            df_temp.index = df.index
            #df_temp = df_temp.reindex(df.index)
            df = pd.concat([df_activity, df_temp, df_meta], axis=1)
            new_header = [str(x) for x in np.arange(df.shape[1] - N_META)] + df.columns[
                df.shape[1] - N_META :
            ].tolist()
            df.columns = new_header

        if step == "HUMIDITYAPPEND":
            df_activity = df.copy().iloc[:, :-N_META]
            #df_activity.index = df.index  # need to keep original sample index!!!!
            df_meta = df.iloc[:, -N_META:]
            #df_hum = df_hum.reindex(df.index)
            df_hum.index = df.index
            df = pd.concat([df_activity, df_hum, df_meta], axis=1)
            new_header = [str(x) for x in np.arange(df.shape[1] - N_META)] + df.columns[
                df.shape[1] - N_META :
            ].tolist()
            df.columns = new_header

        if step == "RAINFALLAPPEND":
            df_activity = df.copy().iloc[:, :-N_META]
            #df_activity.index = df.index  # need to keep original sample index!!!!
            df_meta = df.iloc[:, -N_META:]
            df_rainfall.index = df.index
            #df_rainfall = df_rainfall.reindex(df.index)
            df = pd.concat([df_activity, df_rainfall, df_meta], axis=1)
            new_header = [str(x) for x in np.arange(df.shape[1] - N_META)] + df.columns[
                df.shape[1] - N_META :
            ].tolist()
            df.columns = new_header

        if step == "WINDSPEEDAPPEND":
            df_activity = df.copy().iloc[:, :-N_META]
            #df_activity.index = df.index  # need to keep original sample index!!!!
            df_meta = df.iloc[:, -N_META:]
            df_windspeed.index = df.index
            #df_windspeed = df_windspeed.reindex(df.index)
            df = pd.concat([df_activity, df_windspeed, df_meta], axis=1)
            new_header = [str(x) for x in np.arange(df.shape[1] - N_META)] + df.columns[
                df.shape[1] - N_META :
            ].tolist()
            df.columns = new_header

        if step == "DIFFAPPEND":
            df_activity = df.copy().iloc[:, :-N_META]
            df_meta = df.iloc[:, -N_META:]
            df_diff = pd.DataFrame(
                df_activity.copy().iloc[:, 1440:].values
                - df_activity.copy().iloc[:, :-1440].values
            )
            df = pd.concat(
                [
                    df_activity.reset_index(drop=True),
                    df_diff.reset_index(drop=True),
                    df_meta.reset_index(drop=True),
                ],
                axis=1,
            )
            new_header = [str(x) for x in np.arange(df.shape[1] - N_META)] + df.columns[
                df.shape[1] - N_META :
            ].tolist()
            df.columns = new_header
            df.index = df_activity.index

        if step == "DIFF":
            df_activity = df.copy().iloc[:, :-N_META]
            df_meta = df.iloc[:, -N_META:]
            df_diff = pd.DataFrame(
                df_activity.copy().iloc[:, 1440:].values
                - df_activity.copy().iloc[:, :-1440].values
            )
            df = pd.concat(
                [df_diff.reset_index(drop=True), df_meta.reset_index(drop=True)], axis=1
            )
            new_header = [str(x) for x in np.arange(df.shape[1] - N_META)] + df.columns[
                df.shape[1] - N_META :
            ].tolist()
            df.columns = new_header
            df.index = df_activity.index

        if step == "DIFFLASTD":
            df_activity = df.copy().iloc[:, :-N_META]
            df_meta = df.iloc[:, -N_META:]

            df_last_day = df_activity.copy().iloc[:, -1440:]
            df_last_day = pd.concat([df_last_day] * (days - 1), axis=1)

            df_to_sub = df_activity.copy().iloc[:, :-1441]

            df_diff = pd.DataFrame(df_to_sub.values - df_last_day.values)
            df = pd.concat(
                [df_diff.reset_index(drop=True), df_meta.reset_index(drop=True)], axis=1
            )
            new_header = [str(x) for x in np.arange(df.shape[1] - N_META)] + df.columns[
                df.shape[1] - N_META :
            ].tolist()
            df.columns = new_header
            df.index = df_activity.index

        if step == "DIFFLASTDAPPEND":
            df_activity = df.copy().iloc[:, :-N_META]
            df_meta = df.iloc[:, -N_META:]

            df_last_day = df_activity.copy().iloc[:, -1440:]
            df_last_day = pd.concat([df_last_day] * (days - 1), axis=1)

            df_to_sub = df_activity.copy().iloc[:, :-1441]

            df_diff = pd.DataFrame(df_to_sub.values - df_last_day.values)
            df = pd.concat(
                [
                    df_activity.reset_index(drop=True),
                    df_diff.reset_index(drop=True),
                    df_meta.reset_index(drop=True),
                ],
                axis=1,
            )
            new_header = [str(x) for x in np.arange(df.shape[1] - N_META)] + df.columns[
                df.shape[1] - N_META :
            ].tolist()
            df.columns = new_header
            df.index = df_activity.index

        if step == "TEMPERATURE":
            df_activity = df.copy().iloc[:, :-N_META]
            df_activity.index = df.index  # need to keep original sample index!!!!
            df_meta = df.iloc[:, -N_META:]
            df_temp.index = df.index
            df = pd.concat([df_temp, df_meta], axis=1)
            new_header = [str(x) for x in np.arange(df.shape[1] - N_META)] + df.columns[
                df.shape[1] - N_META :
            ].tolist()
            df.columns = new_header

        if step == "HUMIDITY":
            df_activity = df.copy().iloc[:, :-N_META]
            df_activity.index = df.index  # need to keep original sample index!!!!
            df_meta = df.iloc[:, -N_META:]
            df_hum.index = df.index
            df = pd.concat([df_hum, df_meta], axis=1)
            new_header = [str(x) for x in np.arange(df.shape[1] - N_META)] + df.columns[
                df.shape[1] - N_META :
            ].tolist()
            df.columns = new_header

        if step == "RAINFALL":
            df_activity = df.copy().iloc[:, :-N_META]
            df_activity.index = df.index  # need to keep original sample index!!!!
            df_meta = df.iloc[:, -N_META:]
            df_rainfall.index = df.index
            df = pd.concat([df_rainfall, df_meta], axis=1)
            new_header = [str(x) for x in np.arange(df.shape[1] - N_META)] + df.columns[
                df.shape[1] - N_META :
            ].tolist()
            df.columns = new_header

        if step == "WINDSPEED":
            df_activity = df.copy().iloc[:, :-N_META]
            df_activity.index = df.index  # need to keep original sample index!!!!
            df_meta = df.iloc[:, -N_META:]
            df_windspeed.index = df.index
            df = pd.concat([df_windspeed, df_meta], axis=1)
            new_header = [str(x) for x in np.arange(df.shape[1] - N_META)] + df.columns[
                df.shape[1] - N_META :
            ].tolist()
            df.columns = new_header


        if step in ["STANDARDSCALER", "STDS", "STD"]:
            df.iloc[:, :-N_META] = StandardScaler(
                with_mean=True, with_std=True
            ).fit_transform(df.iloc[:, :-N_META].values)

            # if "TEMPERATURE" not in step_slug and "HUMIDITY" not in step_slug and "PCA" not in step_slug:
            #     if "CWT" in step_slug:
            #         SampleVisualisation(df, CWT_Transform.shape, N_META, graph_outputdir + "/" + step, step_slug, None, None, CWT_Transform.scales)
            #
            #     if "STFT" in step_slug and "PCA" not in step_slug:
            #         SampleVisualisation(df, STFT_Transform.shape, N_META, graph_outputdir + "/" + step, step_slug,
            #                             STFT_Transform.sfft_window, STFT_Transform.stft_time, STFT_Transform.freqs)

        if step == "CENTER":
            df.iloc[:, :-N_META] = CenterScaler(center_by_sample=False).fit_transform(
                df.iloc[:, :-N_META].values
            )
        if step == "CENTER_STD":
            df.iloc[:, :-N_META] = CenterScaler(
                center_by_sample=True, divide_by_std=True
            ).fit_transform(df.iloc[:, :-N_META].values)
        if step == "MINMAX":
            df.iloc[:, :-N_META] = MinMaxScaler().fit_transform(
                df.iloc[:, :-N_META].values
            )
        if step == "L2":
            df.iloc[:, :-N_META] = Normalizer().transform(df.iloc[:, :-N_META].values)
        if step == "ANSCOMBE":
            df.iloc[:, :-N_META] = Anscombe().transform(df.iloc[:, :-N_META].values)
        if step == "SQRT":
            df.iloc[:, :-N_META] = Sqrt().transform(df.iloc[:, :-N_META].values)
        if step == "LOG":
            df.iloc[:, :-N_META] = Log().transform(df.iloc[:, :-N_META].values)
        if step == "QN":
            df.iloc[:, :-N_META] = QuotientNormalizer(
                out_dir=graph_outputdir / step, output_graph=output_qn_graph, enable_qn_peak_filter=False, animal_ids=df["id"].values,
                labels=df["target"].values
            ).transform(df.iloc[:, :-N_META].values)
            df = df.fillna(0)
        if "STFT" in step:
            STFT_Transform = STFT(
                sfft_window=sfft_window,
                out_dir=graph_outputdir / step,
                step_slug=step_slug,
                animal_ids=animal_ids,
                targets=df["health"].tolist(),
                dates=df["date"].tolist(),
            )
            d = STFT_Transform.transform(df.copy().iloc[:, :-N_META].values)
            data_frame_stft = pd.DataFrame(d)
            data_frame_stft.index = df.index  # need to keep original sample index!!!!
            df_meta = df.iloc[:, -N_META:]
            df = pd.concat([data_frame_stft, df_meta], axis=1)
            del data_frame_stft
        if "DWT" in step:
            DWT_Transform = DWT(
                dwt_window=dwt_window,
                out_dir=graph_outputdir / step,
                step_slug=step_slug,
                animal_ids=animal_ids,
                targets=df["health"].tolist(),
                dates=df["date"].tolist(),
            )
            d, _ = DWT_Transform.transform(df.copy().iloc[:, :-N_META].values)
            data_frame_dwt = pd.DataFrame(d)
            data_frame_dwt.index = df.index  # need to keep original sample index!!!!
            df_meta = df.iloc[:, -N_META:]
            df = pd.concat([data_frame_dwt, df_meta], axis=1)
            time_freq_shape = DWT_Transform.shape
            del data_frame_dwt
        if "CWT" in step:
            df_meta = df.iloc[:, -N_META:]
            df_o = df.copy()
            CWT_Transform = CWT(
                wavelet_f0=wavelet_f0,
                out_dir=graph_outputdir / step,
                step_slug=step_slug,
                n_scales=n_scales,
                animal_ids=animal_ids,
                targets=df["health"].tolist(),
                dates=df["date"].tolist(),
                enable_graph_out=enable_graph_out,
                sub_sample_scales=sub_sample_scales,
            )
            data_frame_cwt, _, std_scales = CWT_Transform.transform(
                df.copy().iloc[:, :-N_META].values
            )
            time_freq_shape = CWT_Transform.shape
            data_frame_cwt = pd.DataFrame(data_frame_cwt)
            start_mem = data_frame_cwt.memory_usage().sum() / 1024 ** 2
            gc.collect()
            print('Memory usage of dataframe is {:.2f} MB'.format(start_mem))
            # data_frame_cwt_raw = pd.DataFrame(data_frame_cwt_raw)

            # data_frame_cwt.index = df.index  # need to keep original sample index!!!!
            # df_meta = df.iloc[:, -N_META:]
            # df = pd.concat([data_frame_cwt, df_meta], axis=1)
            # sanity check#################################################################################################
            # wont work sincce using avg of sample!
            # rdm_idxs = random.choices(df.index.tolist(), k=1)
            # samples_tocheck = df_o.loc[(rdm_idxs), :].values[:, :-N_META]
            # cwt_to_check = pd.DataFrame(CWT(out_dir=graph_outputdir + "/" + step + "/cwt_sanity_check/").transform(samples_tocheck))
            # prev_cwt_results = df.loc[(rdm_idxs), :].values[:, :-N_META]
            # assert False not in (cwt_to_check.values == prev_cwt_results), "missmatch in cwt sample!"
            #############################################################################################################

            data_frame_cwt.index = df.index  # need to keep original sample index!!!!
            CWTVisualisation(
                N_META,
                step_slug,
                graph_outputdir,
                CWT_Transform.shape,
                CWT_Transform.coi_mask,
                CWT_Transform.scales,
                CWT_Transform.coi,
                df_o.copy(),
                data_frame_cwt,
                class_healthy_label,
                class_unhealthy_label,
                plot_all_target=plot_all_target,
            )

            data_frame_cwt.index = df.index  # need to keep original sample index!!!!
            df = pd.concat([data_frame_cwt, df_meta], axis=1)
            # CWTVisualisation(step_slug, graph_outputdir, CWT_Transform.shape, CWT_Transform.coi_mask, CWT_Transform.scales, CWT_Transform.coi, df_o.copy(),
            #                  data_frame_cwt_raw, class_healthy_label, class_unhealthy_label, class_healthy, class_unhealthy, filename_sub="real")

            df = df.dropna(axis=1, how="all")  # removes nan from coi
            del data_frame_cwt
            # del data_frame_cwt_raw
        if "STDSCALE" in step:
            print("calculate std for each cwt scale...")
            assert (
                std_scales is not None
            ), "CWT need to be calculated first, make sure that CWT is in the steps array before STDSCALE"
            std_scales.index = df.index  # need to keep original sample index!!!!
            df = pd.concat([std_scales, df_meta], axis=1)
        if "TSNE" in step:
            tsne_dim = int(step[step.find("(") + 1 : step.find(")")])
            print("tsne_dim", tsne_dim)
            df_before_reduction = df.iloc[:, :-N_META].values
            data_frame_tsne = pd.DataFrame(
                TSNE(n_components=tsne_dim).fit_transform(df_before_reduction)
            )
            data_frame_tsne.index = df.index  # need to keep original sample index!!!!
            df_meta = df.iloc[:, -N_META:]
            df = pd.concat([data_frame_tsne, df_meta], axis=1)
            del data_frame_tsne

        if "PCA" in step:
            pca_dim = int(step[step.find("(") + 1 : step.find(")")])
            print("pca_dim", pca_dim)
            df_before_reduction = df.iloc[:, :-N_META].values
            data_frame_pca = pd.DataFrame(
                PCA(n_components=pca_dim).fit_transform(df_before_reduction)
            )
            data_frame_pca.index = df.index  # need to keep original sample index!!!!
            df_meta = df.iloc[:, -N_META:]
            df = pd.concat([data_frame_pca, df_meta], axis=1)
            del data_frame_pca

        if "UMAP" in step:
            df_before_reduction = df.iloc[:, :-N_META].values
            data_frame_umap = pd.DataFrame(
                umap.UMAP().fit_transform(df_before_reduction)
            )
            data_frame_umap.index = df.index  # need to keep original sample index!!!!
            df_meta = df.iloc[:, -N_META:]
            df = pd.concat([data_frame_umap, df_meta], axis=1)
            del data_frame_umap

        if "UPSAMP" in step:
            resolution = 0.7
            df_before_up = df.iloc[:, :-N_META].values
            data_frame_up = pd.DataFrame(resample_s(df_before_up, int(np.ceil(df_before_up.shape[1] / resolution)), axis=1))
            data_frame_up.index = df.index  # need to keep original sample index!!!!
            df_meta = df.iloc[:, -N_META:]
            df = pd.concat([data_frame_up, df_meta], axis=1)


        print("AFTER STEP ->", df)
        # if "CWT" not in step_slug:
        #     plot_distribution(
        #         df.iloc[:, :-N_META].values,
        #         graph_outputdir,
        #         f"data_distribution_after_{step}",
        #     )

    # if "PCA" in step_slug:
    #     plotDistribution(df.iloc[:, :-N_META].values, graph_outputdir, "data_distribution_after_%s" % step_slug)
    targets = df["target"]
    health = df["health"]
    df_with_meta = df.copy()
    if keep_meta:
        df = df.iloc[:, :]
    else:
        df = df.iloc[:, :-N_META]
    df["target"] = targets
    df["health"] = health
    print(df)
    return df, df_with_meta, time_freq_shape


def main():
    print("")


if __name__ == "__main__":
    main()
