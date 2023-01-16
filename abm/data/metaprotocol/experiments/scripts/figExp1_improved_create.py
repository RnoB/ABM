import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os
import json
import glob

# under this path the individual summary statistics are saved
# with _N<number of agents> post tag.
exp_name = "sumfigExp1_nocoll"
data_path = f"/home/david/Desktop/database/ABMFigData/{exp_name}"

# set of agent numbers to summarize for
Ns = [5, 25, 100]
num_patches = [3, 50]

# fonstsize
FS = {'fontsize': 12}

# colors
c_occ = "#0f4f93" # "#dcc04e"  # "#0078df"
c_ide = "#f7d634" #"#8b6795"  # "#76f2a3" "#ff4575" "#c4c028"

line_th=3

# figure shape
fig_shape = [len(Ns), len(num_patches)]
fig, ax = plt.subplots(fig_shape[0], fig_shape[1],
                       constrained_layout=True, figsize=(fig_shape[1] * 4, fig_shape[0] * 4),
                       sharex=False, sharey="row")
gs1 = gridspec.GridSpec(fig_shape[0], fig_shape[1])
gs1.update(wspace=0, hspace=0)

for ni in range(fig_shape[0]):
    N = Ns[ni]
    # Loading data
    # try:
    collapsed_data_occ = np.load(os.path.join(data_path, f"coll_eff_N{N}_occ.npy"))
    collapsed_data_noocc = np.load(os.path.join(data_path, f"coll_eff_N{N}_noocc.npy"))
    collstd_occ = np.load(os.path.join(data_path, f"coll_effstd_N{N}_occ.npy"))
    collstd_noocc = np.load(os.path.join(data_path, f"coll_effstd_N{N}_noocc.npy"))
    # except:
    #     break

    # Finding appropriate columns where number of patches will match
    num_patches_ind_occ = []
    labels = np.loadtxt(os.path.join(data_path, f"coll_eff_N{N}_occ.txt"), dtype=str)
    for li in range(0, len(labels), 2):
        filtered_label = labels[li + 1].replace("N_RESOURCES=", "").replace(".0,", " x ") + labels[li].replace("MIN_RESOURCE_PER_PATCH=", "").replace(".0", "U")
        nup = int(filtered_label.split(" x ")[0])
        if nup in num_patches:
            num_patches_ind_occ.append(int(li/2))
    print(f"In oclluded case will use columns {num_patches_ind_occ}")

    num_patches_ind_noocc = []
    labels = np.loadtxt(os.path.join(data_path, f"coll_eff_N{N}_noocc.txt"), dtype=str)
    for li in range(0, len(labels), 2):
        filtered_label = labels[li + 1].replace("N_RESOURCES=", "").replace(".0,", " x ") + labels[li].replace(
            "MIN_RESOURCE_PER_PATCH=", "").replace(".0", "U")
        nup = int(filtered_label.split(" x ")[0])
        if nup in num_patches:
            num_patches_ind_noocc.append(int(li / 2))
    print(f"In non occluded case will use columns {num_patches_ind_noocc}")

    # Extracting data from collapsed matrices
    lines_occ = collapsed_data_occ[..., num_patches_ind_occ]
    stds_occ = collstd_occ[..., num_patches_ind_occ]
    lines_noocc = collapsed_data_noocc[..., num_patches_ind_noocc]
    stds_noocc = collstd_noocc[..., num_patches_ind_occ]

    for env_i in range(len(num_patches)):
        plt.axes(ax[ni, env_i])
        if ni == 1 and env_i == 1:
            plt.plot(lines_noocc[..., env_i], label=f"Idealized", color=c_ide, linewidth=line_th)
            plt.fill_between([i for i in range(len(lines_noocc[..., env_i]))], lines_noocc[..., env_i] - stds_noocc[..., env_i],
                             lines_noocc[..., env_i] + stds_noocc[..., env_i], alpha=0.3, color=c_ide)
            plt.plot(lines_occ[..., env_i], label=f"Occlusion", color=c_occ, linewidth=line_th, ls="--")
            plt.fill_between([i for i in range(len(lines_occ[..., env_i]))], lines_occ[..., env_i] - stds_occ[..., env_i],
                             lines_occ[..., env_i] + stds_occ[..., env_i], alpha=0.3, color=c_occ)

        else:
            plt.plot(lines_noocc[..., env_i], color=c_ide, linewidth=line_th)
            plt.fill_between([i for i in range(len(lines_noocc[..., env_i]))], lines_noocc[..., env_i] - stds_noocc[..., env_i],
                             lines_noocc[..., env_i] + stds_noocc[..., env_i], alpha=0.3, color=c_ide)
            plt.plot(lines_occ[..., env_i], color=c_occ, linewidth=line_th, ls="--")
            plt.fill_between([i for i in range(len(lines_occ[..., env_i]))], lines_occ[..., env_i] - stds_occ[..., env_i],
                             lines_occ[..., env_i] + stds_occ[..., env_i], alpha=0.3, color=c_occ)


        # Making axis labels
        if ni == 0 and env_i == 0:
            plt.ylabel(f"$N_A$={Ns[ni]}", fontdict=FS)
            plt.title(f"Patchy Environment\n$N_R={num_patches[env_i]}$", fontdict=FS)
            #plt.yticks([i for i in range(len(y_labels))], y_labels, ha='right', rotation_mode='anchor')
        elif ni == 1 and env_i == 0:
            plt.ylabel(f"$N_A$={Ns[ni]}", fontdict=FS)
        elif ni == 0 and env_i == 1:
            plt.title(f"Uniform Environment\n$N_R={num_patches[env_i]}$", fontdict=FS)
        elif env_i == 0:
            plt.ylabel(f"$N_A$={Ns[ni]}", fontdict=FS)
            # Making sparse ticks
            # curr_yticks = list(ax[ni, env_i].get_yticks())
            # sparse_yticks = [curr_yticks[0], curr_yticks[int(len(curr_yticks)/2)], curr_yticks[-1]]
            # print(sparse_yticks)
            # parse_ytick_rotations = [0 for i in range(len(sparse_yticks))]
            # print(parse_ytick_rotations)
            # parse_ytick_rotations[0] = 45
            # parse_ytick_rotations[0] = -45
            # plt.yticks(sparse_yticks, sparse_yticks, ha='right', rotation_mode='anchor')
            # for ticki, tick in enumerate(ax[ni, env_i].get_yticklabels()):
            #     tick.set_rotation(parse_ytick_rotations[ticki])
        if env_i == 1:
            # ax[ni, env_i].yaxis.tick_right()
            ax[ni, env_i].yaxis.set_ticks_position('none')
            pass
        if ni == len(Ns)-1 and env_i == 0:
            # creating y-axis labels
            tuned_env_pattern = os.path.join(data_path, "tuned_env*.json")
            print("Patterns: ", tuned_env_pattern)
            json_files = glob.glob(tuned_env_pattern)
            for json_path in json_files:
                with open(json_path, "r") as f:
                    envvars = json.load(f)
                    x_labels = envvars["DEC_EPSW"]
            plt.xticks([i for i in range(len(x_labels))], x_labels, ha='right', rotation_mode='anchor')
            for ticki, tick in enumerate(ax[ni, env_i].get_xticklabels()):
                tick.set_rotation(45)
        elif ni == len(Ns)-1 and env_i == 1:
            x_labels_sparse = [x_labels[i] for i in range(0, len(x_labels), 2)]
            #plt.xticks([i for i in range(0, len(x_labels), 2)], x_labels_sparse, ha='left', rotation_mode='anchor')
            plt.xticks([i for i in range(len(x_labels))], x_labels, ha='left', rotation_mode='anchor')
            for ticki, tick in enumerate(ax[ni, env_i].get_xticklabels()):
                tick.set_rotation(-45)


    # fig.text(0.06, 0.5, 'common ylabel', ha='center', va='center', rotation='vertical')
    # ax.set_xlabel("Social Excitability ($\epsilon_w$)", fontdict=FS)

    plt.legend()
plt.subplots_adjust(hspace=0, wspace=0, top=0.8, bottom=0.2, left=0.2, right=0.8)
fig.supxlabel('Social Excitability ($\epsilon_w$)', size=FS["fontsize"], y=0.13)
fig.supylabel('Absolute Search Efficiency', size=FS["fontsize"], x=0.08)
plt.show()





#
#     plt.axes(ax[ni])
#     for hi in range(fig_shape[1]):
#
#
#
#
#
#
#         ni = int(wi * fig_shape[1]) + hi
#         if ni < len(Ns):
#             print(hi, wi, ni)
#             plt.axes(ax[wi, hi])
#             collapsed_data = np.load(os.path.join(data_path, f"coll_eff_N{Ns[ni]}.npy"))
#             # # column-wise normalization
#             for coli in range(collapsed_data.shape[1]):
#                 print(f"Normalizing column {coli}")
#                 minval = np.min(collapsed_data[:, coli])
#                 maxval = np.max(collapsed_data[:, coli])
#                 collapsed_data[:, coli] = (collapsed_data[:, coli] - minval) / (maxval - minval)
#             agent_dim = 4
#             im = plt.imshow(collapsed_data, vmin=min_data_val, vmax=max_data_val)
#
#             # creating x-axis and labels
#             # reading original labels with long names
#             labels = np.loadtxt(os.path.join(data_path, f"coll_eff_N{Ns[ni]}.txt"), dtype=str)
#
#             # simplifying and concatenating labels
#             conc_x_labels = []
#             for li in range(0, len(labels), 2):
#                 conc_x_labels.append(labels[li + 1].replace("N_RESOURCES=", "").replace(".0,", " x ") +
#                                      labels[li].replace("MIN_RESOURCE_PER_PATCH=", "").replace(".0", "U"))
#
#             # creating y-axis labels
#             tuned_env_pattern = os.path.join(data_path, "tuned_env*.json")
#             print("Patterns: ", tuned_env_pattern)
#             json_files = glob.glob(tuned_env_pattern)
#             for json_path in json_files:
#                 with open(json_path, "r") as f:
#                     envvars = json.load(f)
#                     y_labels = envvars["DEC_EPSW"]
#
#             # Manually definig the sparified y ticks and their rotations
#             sparse_y_indices = [0, 2, 4, 6, 8]  # int((len(y_labels)-1)/2), len(y_labels)-1]
#             y_tick_rotations = [45, 33.75, 22.5, 11.25, 0, -11.25, -22.5, -33.75, -45]
#             sparese_y_tick_rotations = [45, 0, 0, 0, -45]
#
#             # The first plot is detailed shows all ticks and labels
#             if hi == 0 and wi == 0:
#                 plt.ylabel("Social Excitability ($\epsilon_w$)")
#                 plt.yticks([i for i in range(len(y_labels))], y_labels, ha='right', rotation_mode='anchor')
#                 # for ticki, tick in enumerate(ax[wi, hi].get_yticklabels()):
#                 #     print(ticki, tick)
#                 #     tick.set_rotation(y_tick_rotations[ticki])
#
#             # The others are sparsified for better readability
#             elif hi == 0:
#                 plt.yticks([i for i in sparse_y_indices],
#                            [y_labels[i] for i in sparse_y_indices], ha='right', rotation_mode='anchor')
#                 for ticki, tick in enumerate(ax[wi, hi].get_yticklabels()):
#                     tick.set_rotation(sparese_y_tick_rotations[ticki])
#
#             # The ones in second or other columns have same y axis
#             else:
#                 plt.yticks([], [])
#
#             if hi == 0 and wi == fig_shape[0] - 1:
#                 plt.xlabel("Environment")
#                 plt.xticks([i for i in range(0, len(conc_x_labels), 2)],
#                            [conc_x_labels[i] for i in range(0, len(conc_x_labels), 2)],
#                            ha='right', rotation_mode='anchor')
#             elif wi == fig_shape[0]-1:
#                 plt.xticks([i for i in range(0, len(conc_x_labels), 2)],
#                            [conc_x_labels[i] for i in range(0, len(conc_x_labels), 2)],
#                            ha='right', rotation_mode='anchor')
#             for tick in ax[wi, hi].get_xticklabels():
#                 tick.set_rotation(45)
#         else:
#             plt.axes(ax[wi, hi])
#             plt.yticks([], [])
#             plt.xticks([], [])
#
# # Adding the colorbar
# # [left, bottom, width, height]
# cbaxes = fig.add_axes([0.2, 0.805, 0.6, 0.03])
# # position for the colorbar
# cb = plt.colorbar(im, cax=cbaxes, orientation='horizontal')
# cb.ax.set_xticks([min_data_val, (min_data_val+max_data_val)/2, max_data_val])
# cb.ax.xaxis.set_ticks_position("top")
# cb.ax.xaxis.set_label_position('top')
# cb.ax.set_title('Relative Search Efficiency')
# # fig.colorbar(im, ax=ax.ravel().tolist(), orientation = 'horizontal')
# plt.subplots_adjust(hspace=0, wspace=0, top=0.8, bottom=0.2, left=0.2, right=0.8)
# plt.show()
