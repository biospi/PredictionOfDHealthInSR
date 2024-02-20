import typer
import ml as main_experiment
import ml_cross_farm_validation as cross_farm_validation
import ml_temporal_validation as temporal_validation
from pathlib import Path


def main(
    exp_main: bool = False,
    exp_temporal: bool = False,
    exp_cross_farm: bool = False,
    weather_exp: bool = True,
    output_dir: Path = Path("output_debug_0"),
    delmas_dir_mrnn: Path = None,
    cedara_dir_mrnn: Path = None,
    n_job: int = 6,
    export_hpc_string: bool = False
):
    """Thesis script runs all key experiments for data exploration chapter
    Args:\n
        output_dir: Output directory
    """

    if weather_exp:
        print("experiment 1 (weather): main pipeline")

        steps_list = [
            ["RAINFALL", "STDS"],
            ["QN", "ANSCOMBE", "LOG", "RAINFALLAPPEND", "STDS"],
            ["QN", "ANSCOMBE", "LOG"]
        ]
        for steps in steps_list:
            slug = "_".join(steps)
            for w_day in [84]:
                for cv in ["RepeatedKFold"]:
                        n_imputed_days = 6
                        n_activity_days = 7
                        main_experiment.main(
                            output_dir=output_dir
                            / "main_experiment"
                            / f"delmas_{cv}_{n_imputed_days}_{n_activity_days}_{w_day}_{slug}"
                            / "2To2",
                            dataset_folder=delmas_dir_mrnn,
                            preprocessing_steps=steps,
                            n_imputed_days=n_imputed_days, #need this for preprocessing wont be used for the weather
                            n_activity_days=n_activity_days,
                            n_weather_days=w_day,
                            cv=cv,
                            classifiers=["rbf"],
                            class_unhealthy_label=["2To2"],
                            study_id="delmas",
                            export_fig_as_pdf=False,
                            plot_2d_space=False,
                            pre_visu=False,
                            skip=False,
                            weather_file=Path("weather_data/delmas_south_africa_2011-01-01_to_2015-12-31.csv")
                        )
                        n_imputed_days = 1
                        n_activity_days = 2
                        main_experiment.main(
                            output_dir=output_dir
                            / "main_experiment"
                            / f"cedara_{cv}_{0}_{0}_{w_day}_{slug}"
                            / "2To2",
                            dataset_folder=cedara_dir_mrnn,
                            preprocessing_steps=steps,
                            n_imputed_days=n_imputed_days,
                            n_activity_days=n_activity_days,
                            n_weather_days=w_day,
                            class_unhealthy_label=["2To2"],
                            cv=cv,
                            classifiers=["rbf"],
                            study_id="cedara",
                            plot_2d_space=False,
                            export_fig_as_pdf=False,
                            pre_visu=False,
                            skip=False,
                            export_hpc_string=export_hpc_string,
                            weather_file=Path("weather_data/cedara_south_africa_2011-01-01_to_2015-12-31.csv"
                            )
                        )

    if exp_main:
        print("experiment 1: main pipeline")

        steps_list = [
            # [],
            # ["QN"],
            # ["L2"],
            ["QN", "ANSCOMBE", "LOG", "STDS"],
            # ["QN", "ANSCOMBE", "LOG", "STD"],
            # ["QN", "ANSCOMBE", "LOG", "MINMAX"],
            # ["QN", "ANSCOMBE", "LOG", "CENTER", "CWT", "STD"],
            # ["L2"],
            # ["L2", "ANSCOMBE", "LOG"],
            # ["L2", "ANSCOMBE", "LOG", "STD"],
            # ["L2", "ANSCOMBE", "LOG", "CENTER", "CWT", "STD"],
            # ["L2"],
            # ["QN", "ANSCOMBE", "LOG", "STD"],
            # ["QN", "ANSCOMBE", "LOG", "MINMAX"],
            # ["QN", "ANSCOMBE", "LOG", "CWT", "STD"],
            # ["LINEAR", "QN", "STD"],
            # ["LINEAR", "QN", "ANSCOMBE", "STD"],
            # ["LINEAR", "QN", "LOG", "STD"],
            # ["QN", "ANSCOMBE", "LOG", "RAINFALLAPPEND", "TEMPERATUREAPPEND", "STDS"],
            # ["QN", "ANSCOMBE", "LOG", "HUMIDITYAPPEND", "STDS"],
            # ["QN", "ANSCOMBE", "LOG", "TEMPERATUREAPPEND", "STDS"],
            # ["QN", "ANSCOMBE", "LOG", "RAINFALLAPPEND", "STDS"],
            # ["QN", "ANSCOMBE", "LOG", "WINDSPEEDAPPEND", "STDS"],
            # ["QN", "ANSCOMBE", "LOG"]
            # ["QN", "ANSCOMBE", "LOG", "STDS"],
            # ["QN", "ANSCOMBE", "LOG", "CENTER", "DWT"]
            # ["QN", "ANSCOMBE", "LOG", "STD", "APPEND", "LINEAR", "QN", "ANSCOMBE", "LOG", "CENTER", "DWT"],
            # ["QN", "ANSCOMBE", "LOG", "CENTER", "DWT"],
            # ["QN", "ANSCOMBE", "LOG", "STD", "APPEND", "LINEAR", "QN", "ANSCOMBE", "LOG", "CENTER", "CWTMORL"],
            # ["QN", "ANSCOMBE", "LOG", "CENTER", "CWTMORL"],
            # ["LINEAR", "QN", "LOG", "CENTER", "CWT(MORL)"],
            # ["LINEAR", "QN", "ANSCOMBE", "LOG", "CENTER", "CWT(MORL)", "STD"]
        ]
        for class_unhealthy_label in ["2To2"]:
            for steps in steps_list:
                slug = "_".join(steps)
                for clf in ["rbf"]:
                    for i_day in [7]:
                        for a_day in [7]:
                            for cv in ["RepeatedKFold"]:
                                for dataset in [
                                    delmas_dir_mrnn,
                                    cedara_dir_mrnn,
                                ]:
                                    farm_id = "delmas"
                                    if "cedara" in str(dataset).lower():
                                        farm_id = "cedara"
                                    main_experiment.main(
                                        output_dir=output_dir
                                        / "main_experiment"
                                        / clf
                                        / dataset.stem
                                        / f"{dataset.stem}_{farm_id}_{cv}_{i_day}_{a_day}_{slug}"
                                        / class_unhealthy_label,
                                        dataset_folder=dataset,
                                        preprocessing_steps=steps,
                                        n_imputed_days=i_day,
                                        n_activity_days=a_day,
                                        cv=cv,
                                        classifiers=[clf],
                                        class_unhealthy_label=[
                                            class_unhealthy_label
                                        ],
                                        study_id=farm_id,
                                        export_fig_as_pdf=False,
                                        plot_2d_space=False,
                                        pre_visu=False,
                                        export_hpc_string=export_hpc_string,
                                        skip=False,
                                        n_job=n_job,
                                    )

    if exp_temporal:
        print("experiment 2: temporal validation")
        i = 7
        n_a = 6
        temporal_validation.main(
            output_dir=output_dir
            / "temporal_validation"
            / f"delmas_{i}_{n_a}"
            / "2To2",
            dataset_folder=delmas_dir_mrnn,
            n_imputed_days=i,
            n_activity_days=n_a,
            export_fig_as_pdf=True,
        )

        # i = 7
        # n_a = 6
        # temporal_validation.main(
        #     output_dir=output_dir / "temporal_validation" / f"cedara_{i}_{n_a}" / "2To2",
        #     dataset_folder=cedara_dir,
        #     n_imputed_days=i,
        #     n_activity_days=n_a,
        #     sample_date_filter="2013-02-14",
        #     class_healthy_label=["1To1"],
        #     class_unhealthy_label=["2To2", "2To4", "3To4", "1To4", "1To3", "4To5", "2To3"],
        #     export_fig_as_pdf=True)

    if exp_cross_farm:
        print("experiment 3: cross farm validation")
        for imp_d in [7]:
            for a_act_day in [1, 4, 7]:
                cross_farm_validation.main(
                    farm1_path=delmas_dir_mrnn,
                    farm2_path=cedara_dir_mrnn,
                    output_dir=output_dir
                    / "cross_farm"
                    / f"{imp_d}_{a_act_day}"
                    / "2To2",
                    n_imputed_days=imp_d,
                    n_activity_days=a_act_day,
                    class_unhealthy_f2=["2To2"],
                )

                # cross_farm_validation.main(
                #     farm1_path=Path("E:\Data2\debug3\delmas\dataset4_mrnn_7day"),
                #     farm2_path=Path("E:\Data2\debug3\cedara\dataset6_mrnn_7day"),
                #     output_dir=output_dir
                #     / "cross_Farm"
                #     / f"{imp_d}_{a_act_day}"
                #     / "4To4_3To5_4To3_5To3_2To5_2To2",
                #     n_imputed_days=imp_d,
                #     n_activity_days=a_act_day,
                #     class_unhealthy_f2=[
                #         "4To4",
                #         "3To5",
                #         "4To3",
                #         "5To3",
                #         "2To5",
                #         "2To2",
                #     ],
                # )


if __name__ == "__main__":
    main(delmas_dir_mrnn=Path("datasets/delmas_dataset4_mrnn_7day"),
         cedara_dir_mrnn=Path("datasets/cedara_datasetmrnn7_23"))
    # typer.run(main)
