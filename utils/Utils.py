import gc
import os

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt

"""
Utility class for static methods
"""


def anscombe(arr, sigma_sq=0, alpha=1):
    """
    Generalized Anscombe variance-stabilizing transformation
    References:
    [1] http://www.cs.tut.fi/~foi/invansc/
    [2] M. Makitalo and A. Foi, "Optimal inversion of the generalized
    Anscombe transformation for Poisson-Gaussian noise", IEEE Trans.
    Image Process, 2012
    [3] J.L. Starck, F. Murtagh, and A. Bijaoui, Image  Processing
    and Data Analysis, Cambridge University Press, Cambridge, 1998)
    :param arr: variance-stabilized signal
    :param sigma_sq: variance of the Gaussian noise component
    :param alpha: scaling factor of the Poisson noise component
    :return: variance-stabilized array
    """
    v = np.maximum((arr / alpha) + (3. / 8.) + sigma_sq / (alpha ** 2), 0)
    f = 2. * np.sqrt(v)
    return f


def inverse_anscombe(arr, sigma_sq=0, m=0, alpha=1, method='closed-form'):
    """
    Inverse of the Generalized Anscombe variance-stabilizing
    transformation
    References:
    [1] http://www.cs.tut.fi/~foi/invansc/
    [2] M. Makitalo and A. Foi, "Optimal inversion of the generalized
    Anscombe transformation for Poisson-Gaussian noise", IEEE Trans.
    Image Process, 2012
    [3] J.L. Starck, F. Murtagh, and A. Bijaoui, Image  Processing
    and Data Analysis, Cambridge University Press, Cambridge, 1998)


    :param arr: variance-stabilized signal
    :param sigma_sq: variance of the Gaussian noise component
    :param m: mean of the Gaussian noise component
    :param alpha: scaling factor of the Poisson noise component
    :param method: 'closed_form' applies the closed-form approximation
    of the exact unbiased inverse. 'asym' applies the asymptotic
    approximation of the exact unbiased inverse.
    :return: inverse variance-stabilized array
    """
    sigma_sq /= alpha ** 2

    if method == 'closed-form':
        # closed-form approximation of the exact unbiased inverse:
        arr_trunc = np.maximum(arr, 0.8)
        inverse = ((arr_trunc / 2.) ** 2 + 0.25 * np.sqrt(1.5) * arr_trunc ** -1 - (11. / 8.) * arr_trunc ** -2 +
                   (5. / 8.) * np.sqrt(1.5) * arr_trunc ** -3 - (1. / 8.) - sigma_sq)
    elif method == 'asym':
        # asymptotic approximation of the exact unbiased inverse:
        inverse = (arr / 2.) ** 2 - 1. / 8 - sigma_sq
        # inverse = np.maximum(0, inverse)
    else:
        raise NotImplementedError('Only supports the closed-form')

    if alpha != 1:
        inverse *= alpha

    if m != 0:
        inverse += m

    return inverse


def center_signal(y, avg):
    y_centered = y - avg
    return y_centered


def create_rec_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))


def plot_heatmap(X1, y1, X2, y2, out_dir, p1_start, p1_end, p2_start, p2_end):
    healthy_samples1 = X1[y1 == 1]
    unhealthy_samples1 = X1[y1 != 1]

    healthy_samples2 = X2[y2 == 1]
    unhealthy_samples2 = X2[y2 != 1]

    fig = make_subplots(
        rows=4,
        cols=1,
        subplot_titles=(f"healthy samples from {p1_start} to {p1_end}", f"unhealthy samples {p1_start} {p1_end}",
                        f"healthy samples {p2_start} to {p2_end}", f"unhealthy samples {p2_start} to {p2_end}"),
        y_title="",
        x_title="Time (1 min bins)",
    )

    trace1 = go.Heatmap(
        z=healthy_samples1,
        x=np.arange(0, healthy_samples1.shape[0], 1),
        y=np.arange(0, healthy_samples1.shape[1], 1),
        colorscale="Viridis",
        showscale=False
    )
    fig.append_trace(trace1, row=1, col=1)

    trace2 = go.Heatmap(
        z=unhealthy_samples1,
        x=np.arange(0, unhealthy_samples1.shape[0], 1),
        y=np.arange(0, unhealthy_samples1.shape[1], 1),
        colorscale="Viridis",
        showscale=False
    )
    fig.append_trace(trace2, row=2, col=1)

    trace3 = go.Heatmap(
        z=healthy_samples2,
        x=np.arange(0, healthy_samples2.shape[0], 1),
        y=np.arange(0, healthy_samples2.shape[1], 1),
        colorscale="Viridis",
        showscale=False
    )
    fig.append_trace(trace3, row=3, col=1)

    trace4 = go.Heatmap(
        z=unhealthy_samples2,
        x=np.arange(0, unhealthy_samples2.shape[0], 1),
        y=np.arange(0, unhealthy_samples2.shape[1], 1),
        colorscale="Viridis",
        showscale=False
    )
    fig.append_trace(trace4, row=4, col=1)

    out_dir.mkdir(parents=True, exist_ok=True)
    filename = "samples_heatmap.html"
    output = out_dir / filename
    print(output)
    fig.write_html(str(output))


def getXY(df):
    print(df)
    X = df.iloc[:, :-2].values
    y = df["health"].values
    return X, y


def binarize(tagets, healty_target=1):
    return (tagets != healty_target).astype(int)


def concatenate_images(images_list, out_dir, filename="cwt_mean_per_label.png"):
    imgs = [Image.open(str(i)) for i in images_list]

    # If you're using an older version of Pillow, you might have to use .size[0] instead of .width
    # and later on, .size[1] instead of .height
    min_img_width = min(i.width for i in imgs)

    total_height = 0
    for i, img in enumerate(imgs):
        # If the image is larger than the minimum width, resize it
        if img.width > min_img_width:
            imgs[i] = img.resize((min_img_width, int(img.height / img.width * min_img_width)), Image.ANTIALIAS)
        total_height += imgs[i].height

    # I have picked the mode of the first image to be generic. You may have other ideas
    # Now that we know the total height of all of the resized images, we know the height of our final image
    img_merge = Image.new(imgs[0].mode, (min_img_width, total_height))
    y = 0
    for img in imgs:
        img_merge.paste(img, (0, y))

        y += img.height

    file_path = out_dir.parent / filename
    print(file_path)
    img_merge.save(str(file_path))


def ninefive_confidence_interval(x):
    # boot_median = [np.median(np.random.choice(x, len(x))) for _ in range(iteration)]
    x.sort()
    lo_x_boot = np.percentile(x, 2.5)
    hi_x_boot = np.percentile(x, 97.5)
    # print(lo_x_boot, hi_x_boot)
    return lo_x_boot, hi_x_boot


def explode(df, lst_cols, fill_value=''):
    # make sure `lst_cols` is a list
    if lst_cols and not isinstance(lst_cols, list):
        lst_cols = [lst_cols]
    # all columns except `lst_cols`
    idx_cols = df.columns.difference(lst_cols)

    # calculate lengths of lists
    lens = df[lst_cols[0]].str.len()

    if (lens > 0).all():
        # ALL lists in cells aren't empty
        return pd.DataFrame({
            col:np.repeat(df[col].values, df[lst_cols[0]].str.len())
            for col in idx_cols
        }).assign(**{col:np.concatenate(df[col].values) for col in lst_cols}) \
          .loc[:, df.columns]
    else:
        # at least one list in cells is empty
        return pd.DataFrame({
            col:np.repeat(df[col].values, df[lst_cols[0]].str.len())
            for col in idx_cols
        }).assign(**{col:np.concatenate(df[col].values) for col in lst_cols}) \
          .append(df.loc[lens==0, idx_cols]).fillna(fill_value) \
          .loc[:, df.columns]

def explode(df, columns):
    df['tmp'] = df.apply(lambda row: list(zip(row[columns])), axis=1)
    df = df.explode('tmp')
    df[columns] = pd.DataFrame(df['tmp'].tolist(), index=df.index)
    df.drop(columns='tmp', inplace=True)
    print(df)
    return df


def reduce_mem_usage(df, int_cast=False, obj_to_category=False, subset=None):
    """
    Iterate through all the columns of a dataframe and modify the data type to reduce memory usage.
    :param df: dataframe to reduce (pd.DataFrame)
    :param int_cast: indicate if columns should be tried to be casted to int (bool)
    :param obj_to_category: convert non-datetime related objects to category dtype (bool)
    :param subset: subset of columns to analyse (list)
    :return: dataset with the column dtypes adjusted (pd.DataFrame)
    """
    start_mem = df.memory_usage().sum() / 1024 ** 2
    gc.collect()
    print('Memory usage of dataframe is {:.2f} MB'.format(start_mem))

    cols = subset if subset is not None else df.columns.tolist()

    for col in tqdm(cols):
        col_type = df[col].dtype

        if col_type != object and col_type.name != 'category' and 'datetime' not in col_type.name:
            c_min = df[col].min()
            c_max = df[col].max()

            # test if column can be converted to an integer
            treat_as_int = str(col_type)[:3] == 'int'
            # if int_cast and not treat_as_int:
            #     treat_as_int = check_if_integer(df[col])

            if treat_as_int:
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.uint8).min and c_max < np.iinfo(np.uint8).max:
                    df[col] = df[col].astype(np.uint8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.uint16).min and c_max < np.iinfo(np.uint16).max:
                    df[col] = df[col].astype(np.uint16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.uint32).min and c_max < np.iinfo(np.uint32).max:
                    df[col] = df[col].astype(np.uint32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
                elif c_min > np.iinfo(np.uint64).min and c_max < np.iinfo(np.uint64).max:
                    df[col] = df[col].astype(np.uint64)
            else:
                if c_min > np.finfo(float).min and c_max < np.finfo(float).max:
                    df[col] = df[col].astype(float)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
        elif 'datetime' not in col_type.name and obj_to_category:
            df[col] = df[col].astype('category')
    gc.collect()
    end_mem = df.memory_usage().sum() / 1024 ** 2
    print('Memory usage after optimization is: {:.3f} MB'.format(end_mem))
    print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))

    return df