import matplotlib.pyplot as plt
import argparse
import os
import requests

THIS_DIR=os.path.dirname(os.path.abspath(__file__))

def parser():
	parse = argparse.ArgumentParser("generateChart")
	parse.add_argument("--output_dir", "-od",  help="Output Directory", default=f"{THIS_DIR}/../build", type=str)
	parse.add_argument("--templates_dir", "-td",  help="Templates Directory", default=f"{THIS_DIR}/../templates", type=str)
	parse.add_argument("--project", "-p",  help="Project Name", required=True, type=str)
	return parse

def main(**kwargs):
	if not os.path.isdir(kwargs.get('output_dir')):
		os.makedirs(kwargs.get('output_dir'))
	result = requests.get(f'http://127.0.0.1:8000/get_weekly/{kwargs["project"]}')
	new_data = result.json()
	new_data["x_axis"] = "DATE"
	new_data["y_axis"] = "TOTAL"
	new_data["chart"] = ["TOTAL","PASSED","FAILED"]
	graph_path = f"{kwargs.get('output_dir')}/chart.jpeg"
	project = new_data['RESULT']
	project_list = []

	for key in project[0] :
		project_list.append(key)

	data_dic = {}
	#create dic_list
	for j in range(len(project_list)):
		if project_list[j] == 'DATE':
			data_dic[project_list[j]] = []
			for data in project:
				today_date = str
				temp_list = data['DATE'].split('-')
				today_date = str(temp_list[1]) + '.' + str(temp_list[2])
				data_dic[project_list[j]].append(today_date)
		else :
			data_dic[project_list[j]] = []
			for i in range(0,len(project)):
				data_dic[project_list[j]].append(int(project[i][project_list[j]]))


	#graph
	plt.style.use(['seaborn'])
	color = ['#009543','#0047BD', '#C8707E', '#C8707E', 0]

	#size
	fig = plt.figure(figsize=(14,7))
	ax1 = fig.add_subplot(2,1,1)
	ax2 = fig.add_subplot(2,1,2)

	#graph(shift)
	ax1.spines['right'].set_visible(False)
	ax1.spines['top'].set_visible(False)
	ax2.spines['right'].set_visible(False)
	ax2.spines['top'].set_visible(False)

	#graph(all)
	for j in range(len(project_list)):
		if project_list[j] != 'DATE':
			ax1.plot(data_dic['DATE'][-10:], data_dic[project_list[j]][-10:], marker='^',markersize=2,
			markeredgewidth=3, color = color[j], linestyle = 'solid', linewidth = 2, label = project_list[j])

			ax2.plot(data_dic['DATE'], data_dic[project_list[j]], marker='o',markersize=2,
			 markeredgewidth=3, color = color[j], linestyle = 'solid',
			linewidth = 2, label = project_list[j])

	#xaxis
	ax2.xaxis.set_ticks([data_dic['DATE'][i] for i in (0, -1)])

	#footnote
	ax1.legend(loc='upper left', fontsize=8)
	ax2.legend(loc='upper left', fontsize=8)

	ax1.set_title(new_data['PROJECT']+'(The last 10 weeks)',fontsize=13)
	ax2.set_title(new_data['PROJECT']+'(weekly)',fontsize=13)
	ax1.tick_params(axis="x",labelsize=9)
	ax2.tick_params(axis="x",labelsize=9)

	plt.savefig(graph_path, dpi = 75)


if __name__ == '__main__':
	args = parser().parse_args()
	main(**vars(args))