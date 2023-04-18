from django.shortcuts import (get_object_or_404,
                              render,
                              HttpResponseRedirect)
from . import models
from django.views.generic import TemplateView
from django.http import HttpResponse, Http404, JsonResponse
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Max, F, Count
import json
from django.utils import timezone
import os, subprocess
from django.conf import settings
from django.db.models import Q
import time

timestamp = int(time.time())

"""
Render Main HTML Data

index(request)            : submenu.html      (html side_menu)
detail(request, number)   : testlist.html     (render 'models.TestList')
cases(request, number)    : testcase.html     (render 'models.TestCase' each TestCase_Detail lastest data)
weekly(request, project)  : weeklychart.html  (render 'models.WeeklyTable')
failed(request, number)   : failedlist.html   (render 'models.TestCase' each TestCase_Detail Result=failed)
"""
# submenu.html
def index(request):
  content = {}
  content['timestamp'] = timestamp
  projects = models.Project.objects.all()
  content['Completed'] = projects.filter(Completed=1)
  content['Ongoing'] = projects.exclude(Completed=1)
  for each in range(0,len(content['Ongoing'])):
    testlist = models.TestList.objects.filter(Project=content['Ongoing'][each], Used=1)
    total_passed = total = ratio = 0

    dut_list = (subprocess.check_output(f"ls ", cwd=os.path.join(settings.EXTERNAL_DIR, content['Ongoing'][each].ProjectName, 'latest'), shell=True).decode('utf-8')).replace("\n"," ").split(" ")
    dut_list = [ each for each in dut_list if each != ""]
    for each2 in testlist:
      passed, failed, running, pending = each2.latest()
      total_passed += passed
      total += passed + failed + running + pending
    try:
      ratio = round(total_passed / total * 100)
    except ZeroDivisionError:
      ratio = 0
    content['Ongoing'][each].ratio = ratio
    content['Ongoing'][each].dut_list = dut_list
  return render(request,'main/submenu.html', content)

# testlist.html
def detail(request, number):
  project_name = models.Project.objects.get(pk=number)
  testlist = models.TestList.objects.filter(Project_id=number, Used=1).order_by('ListName')
  for each in testlist:
    passed, failed, running, pending = each.latest()
    each.passed_cases = passed
    each.failed_cases = failed
    each.runing_cases = running
    each.pending_cases = pending
    each.total_cases = passed + failed + running + pending

  weeklyData = models.WeeklyTable.objects.filter(ProjectName=project_name.ProjectName).last()

  return render (request, 'main/testlist.html', {
    'testlist' : testlist,
    'project'  : project_name,
    'end_date' : weeklyData.datetime.strftime("%Y-%m-%d"),
    'end_commit' : weeklyData.commit,
    'timestamp' : timestamp
    })

# testcase.html
def cases(request, number):
  testcases = models.TestCase.objects.filter(TestList_id=number, Used=1)
  data = [each.latest() for each in testcases]
  for each in range(len(data)):
    if data[each].Result == "SLRUM_FAILED_QUEUE":
      # print(data[each].Result)
      data[each].Result = "C_FAILED"
  return render (request, 'main/testcase.html', {'testcase' : data, 'timestamp':timestamp})

# weeklychart.html
def weekly(request, project):
  weeklyData = models.WeeklyTable.objects.filter(ProjectName=project).order_by('datetime')
  weeklyData_desc = models.WeeklyTable.objects.filter(ProjectName=project).order_by('-datetime')
  temp = weeklyData.values('Passed', 'Failed', 'Total', 'datetime')
  passed = []
  failed = []
  total = []
  datetime = []

  for each in temp:
    passed.append(str(each.get('Passed')))
    failed.append(str(each.get('Failed')))
    total.append(str(each.get('Total')))
    datetime.append(str(each.get('datetime')))
  return render (request, 'main/weeklychart.html', {'weeklyData': weeklyData_desc, 'passed' : passed, 'failed' : failed, 'total' : total, 'datetime' : datetime, 'project':project})

# failedlist.html
def failed(request, number) :
  project_name = models.Project.objects.get(pk=number)
  testcases = models.TestCase.objects.filter(TestList__Project_id=number, TestList__Used=1, Used=1)
  data = [each.latest() for each in testcases]
  obj = []
  for detail in data:
    if detail.Result == "FAILED" or detail.Result == "C_FAILED" or detail.Result == "SLRUM_FAILED" or detail.Result == "SLRUM_FAILED_QUEUE":
      obj.append(detail)
  return render (request, 'main/failedlist.html', {'project'  : project_name, 'failedlist' : obj, 'timestamp': timestamp})


"""
Django Rest API

jenkins_full(request)           : Add New 'TestList', 'TestCase', 'TestCase_Detail' Data
jenkins_simulation(request)     : Update 'TestCase_Detail' Result (RUNNING, PASSED, FAILED, SLRUM_FAILED, FAILED, C_FAILED, SLRUM_FAILED_QUEUE)
get_report(request, project)    : For ld_dashboard_email return latest Total Result
get_weekly(request, project)    : For ld_dashboard_email return 'WeeklyTable' Result
get_receivers(request, project) : For ld_dashboard_email return 'Project' -> 'User List'
update_weekly(request, project) : Update 'WeeklyTable'
delete(request)                 : Delete all data on a specific date
"""
@csrf_exempt
def jenkins_full(request):
# curl -X POST -H 'Content-Type: application/json' -d '{"project" : "tmp_project", "test" : [{"test_list" : "tmp_list1","name" : "tmp_case1","dut" : "FULL"}, ... }' http://127.0.0.1:8000/jenkins_full/
  if request.method == 'POST':
    data = json.loads(request.body)
    project_name = data.get('project')
    test_results = data.get('test')
    project = get_object_or_404(models.Project, ProjectName=project_name)
    existing_testlists = models.TestList.objects.filter(Project=project)
    existing_testcases=models.TestCase.objects.filter(TestList__in=existing_testlists)
    existing_testcases.update(Used=0)
    existing_testlists.update(Used=0)
    for result in test_results:
        list_name = result.get('test_list')
        case_name = result.get('name')
        dut_name = result.get('dut')
        test_list, created = models.TestList.objects.get_or_create(Project=project, ListName=list_name, DutName=dut_name)
        if created:
            test_list.Used = 1
        else:
            test_list.Used = 1
        test_list.save()
        test_case, created = models.TestCase.objects.get_or_create(TestList=test_list, CaseName=case_name)
        if created:
          test_case.Used = 1
        else:
          test_case.Used = 1
        test_case.save()
        build_date = timezone.now().date()
        models.TestCase_Detail.objects.create(TestCase=test_case, Result='PENDING', BuildDate=build_date)

    return JsonResponse({'message': 'Test results updated successfully.'})
  else:
    return JsonResponse({'message': 'Invalid request method.'})

@csrf_exempt
def jenkins_simulation(request):
# curl -X POST -H 'Content-Type: application/json' -d '{"project" : "tmp_project","test_list" : "tmp_list1","name" : "tmp_case1","Result" : "RUNNING","SimPath" : "/home/aaron/tmp_case1"}' http://127.0.0.1:8000/jenkins_simulation/
  if request.method == 'POST':
    data = json.loads(request.body)
    project_name = data.get('project')
    list_name = data.get('test_list')
    case_name = data.get('name')
    result = data.get('Result')
    project = get_object_or_404(models.Project, ProjectName=project_name)
    testlist = models.TestList.objects.get(Project=project, ListName=list_name)
    testcase = models.TestCase.objects.get(TestList=testlist, CaseName=case_name)
    testcase_detail = models.TestCase_Detail.objects.filter(Canceled=0, TestCase=testcase).last()
    testcase_detail = models.TestCase_Detail.objects.filter(id=testcase_detail.id)
    print(f"TestCase id = {testcase_detail.values_list('id', flat=True).last()}")

    tmp_dict = {}
    for each in ['Command', 'SimPath', 'Result', 'Commit']:
      tmp_dict[each] =  list(testcase_detail.values_list(each, flat=True))[0]
      if each in data.keys():
        tmp_dict[each] =  data.get(each)
    if result=='RUNNING':
      tmp_dict['StartDate']=timezone.now()
    elif result=='PASSED' or result=='FAILED' or result=='SLRUM_FAILED' or result=='C_FAILED' or result=='SLRUM_FAILED_QUEUE':
      tmp_dict['EndDate']=timezone.now()

    testcase_detail.update(**tmp_dict)

    return JsonResponse({'message': 'Test results updated successfully.','key' : testcase_detail.values_list('id', flat=True).last()})
  else:
    return JsonResponse({'message': 'Invalid request method.'})

def get_report(request, project):
# curl http://127.0.0.1:8000/get_report/tmp_project1
  if request.method == 'GET':
    project_q = get_object_or_404(models.Project, ProjectName=project)
    existing_testlists = models.TestList.objects.filter(Project=project_q, Used=1)
    buf_test_lists = { each.replace(f"{project}.","") : {
      'TOTAL' : 0,
      'PASSED' : 0,
      'FAILED' : 0,
      'RUNNING' : 0,
      'PROGRESS' : 0,
      'TEST_CASES' : {
        'PASSED_TEST_LISTS' : [],
        'FAILED_TEST_LISTS' : [],
        'RUNNING_TEST_LISTS' : []
        }
      } for each in [ str(each_in) for each_in in existing_testlists] }

    print(buf_test_lists)
    test_list_dut = {}
    for each in models.TestList.objects.filter(Project_id=project_q.id, Used=1):
      if not test_list_dut.get(each.DutName):
        test_list_dut.update( {str(each.DutName) : []} )
      test_list_dut[each.DutName].append(each.ListName)

    testcases = models.TestCase.objects.filter(TestList__Project_id=project_q.id,  TestList__Used=1, Used=1)
    data = [each.latest() for each in testcases]
    for each in data:
      test_list = str(each.TestCase).split(".")[0]
      if buf_test_lists.get(test_list):
        if   each.Result == 'PASSED':
          buf_test_lists[test_list]['TEST_CASES']['PASSED_TEST_LISTS'].append( { 'name' : str(each.TestCase).split(".")[1] , 'commit' : each.Commit} )
        elif each.Result == 'PENDING' or each.Result == 'RUNNING':
          buf_test_lists[test_list]['TEST_CASES']['RUNNING_TEST_LISTS'].append( { 'name' : str(each.TestCase).split(".")[1] , 'commit' : each.Commit} )
        else:
          buf_test_lists[test_list]['TEST_CASES']['FAILED_TEST_LISTS'].append( { 'name' : str(each.TestCase).split(".")[1] , 'commit' : each.Commit, 'reason' : each.Result} )

    for key, value in buf_test_lists.items():
      buf_test_lists[key].update(
        TOTAL = sum( [ len(x) for x in value.get('TEST_CASES').values() ] ),
        PASSED = len( (value.get('TEST_CASES')).get('PASSED_TEST_LISTS') ),
        RUNNING = len( (value.get('TEST_CASES')).get('RUNNING_TEST_LISTS') ),
        FAILED = len( (value.get('TEST_CASES')).get('FAILED_TEST_LISTS') )
      )
      buf_test_lists[key].update( PROGRESS = int(buf_test_lists[key].get('PASSED') * 100 / buf_test_lists[key].get('TOTAL')) )
    p_total    = sum([ each_total['TOTAL'] for each_total in buf_test_lists.values() ])
    p_passed   = sum([ each_total['PASSED'] for each_total in buf_test_lists.values() ])
    p_failed   = sum([ each_total['FAILED'] for each_total in buf_test_lists.values() ])
    p_progress = int(p_passed*100/p_total)

    return JsonResponse({
      'PROJECT' : project,
      'PROJECT_TOTAL'    : p_total,
      'PROJECT_PASSED'   : p_passed,
      'PROJECT_FAILED'   : p_failed,
      'PROJECT_PROGRESS' : p_progress,
      'PROJECT_DUT_CASE' : test_list_dut,
      'LATEST_RESULT' : buf_test_lists
      })
  else:
    return JsonResponse({'TEST_FAILED' : request.method, 'PROJECT' : project })

def get_weekly(request, project):
# curl http://127.0.0.1:8000/get_weekly/tmp_project1
  if request.method == 'GET':
    project_q = get_object_or_404(models.Project, ProjectName=project)
    weekly_data = models.WeeklyTable.objects.filter(ProjectName=project_q.ProjectName).order_by('datetime')
    tmp_json = {
      "PROJECT" : project,
      "RESULT" : [
        {
         "TOTAL" : each.Total,
         "PASSED" : each.Passed,
         "FAILED" : each.Failed,
         "DATE": each.datetime
         } for each in weekly_data
      ]
    }
    return JsonResponse(tmp_json)
  else:
    return JsonResponse({'message': 'Invalid request method.'})

def get_receivers(request, project):
# curl http://127.0.0.1:8000/get_receivers/tmp_project1
  if request.method == 'GET':
    project_q = get_object_or_404(models.Project, ProjectName=project)
    receivers_list = json.loads(project_q.User_List)
    return JsonResponse({'receivers_list' : receivers_list})
  else:
    return JsonResponse({'message': 'Invalid request method.'})

@csrf_exempt
def update_weekly(request, project):
  if request.method == 'POST':
    project_q = get_object_or_404(models.Project, ProjectName=project)
    testcases = models.TestCase.objects.filter(TestList__Project_id=project_q.id,  TestList__Used=1, Used=1)
    test_result = [ each.Result for each in [each.latest() for each in testcases] ]
    this_weeklyData = models.WeeklyTable(
      Total = len(test_result) ,
      Passed = test_result.count("PASSED") ,
      Failed = len(test_result) - test_result.count("PASSED") ,
      datetime = timezone.now() ,
      ProjectName = project,
    )

    this_weeklyData.save()

    return HttpResponse("Success")
  else:
    return Http404

def get_slurm_queue_failed(request, project):
  if request.method == 'GET':
    response_json = {}
    failed_list = json.loads(get_report(request=request, project=project).content)
    for key, value in failed_list.get('LATEST_RESULT').items():
      temp = [ each_test.get('name') for each_test in value.get('TEST_CASES').get('FAILED_TEST_LISTS') if each_test.get('reason') == "SLURM_FAILED_QUEUE" ]
      all_temp = temp
      if len(all_temp) > 0:
        response_json.update( { key : all_temp } )

    print(response_json)
    return JsonResponse({ 'RE_RUN' : response_json })
  else:
    return JsonResponse({'message': 'Invalid request method.'})

@csrf_exempt
def delete(request):
# curl -X POST -H 'Content-Type: application/json' -d '{"project" : "tmp_project1","date" : "2023-04-14"}' http://127.0.0.1:8000/delete/
  if request.method == 'POST':
    data = json.loads(request.body)
    project_name = data.get('project')
    build_date = data.get('date')
    project = get_object_or_404(models.Project, ProjectName=project_name)

    # 해당 날짜 testcase_detail 삭제
    testcase_details = models.TestCase_Detail.objects.filter(TestCase__TestList__Project=project, BuildDate=build_date)
    count_details = testcase_details.count()
    testcase_details.delete()

    # TestCase_detail이 존재하지 않는 Testcase 삭제
    testcases = models.TestCase.objects.annotate(num_details=Count('testcase_detail')).filter(num_details=0, TestList__Project=project)
    count_cases = testcases.count()
    testcases.delete()

    # TestCase가 존재하지 않는 TestList 삭제
    testlists = models.TestList.objects.annotate(num_cases=Count('testcase')).filter(num_cases=0, Project=project)
    count_lists = testlists.count()
    testlists.delete()
    return JsonResponse({ 'message': f'{count_lists} Lists, {count_cases} Cases, {count_details} Details are deleted'})
  else:
    return JsonResponse({'message': 'Invalid request method.'})


"""
Get Previous Data

index_selectbox(request, num)                 : submenu.html    (Add build_date selectbox on submenu.html)
get_previous(request, num, build_date)        : testlist.html   (Get All 'TestList' data for that build_date)
previous_cases(request, number, build_date)   : testcase.html   (Get All 'TestCase' data for that build_date)
"""

def index_selectbox(request, num):
  details = models.TestCase_Detail.objects.filter(TestCase__TestList__Project_id=num)
  build_dates = list(details.exclude(BuildDate=None).values_list('BuildDate', flat=True).distinct().order_by('-BuildDate'))
  formatted_dates = [d.strftime("%Y-%m-%d") for d in build_dates]
  return JsonResponse({'build_dates' : formatted_dates})

def get_previous(request, num, build_date):
  project_name = models.Project.objects.get(pk=num)
  testlist = models.TestList.objects.filter(Project_id=num).order_by('ListName')
  for each in testlist:
    passed, failed, running, pending = each.previous(build_date)
    each.passed_cases = passed
    each.failed_cases = failed
    each.runing_cases = running
    each.pending_cases = pending
    each.total_cases = passed + failed + running + pending
  testlist = filter(lambda x : x.total_cases != 0, testlist)
  return render (request, 'main/testlist.html', {
    'testlist' : testlist,
    'project'  : project_name,
    'previous' : 'previous',
    'build_date' : build_date,
    'timestamp' : timestamp
    })

def previous_cases(request, number, build_date):
  testcases = models.TestCase.objects.filter(TestList_id=number)
  data = [each.previous(build_date) for each in testcases if each.previous(build_date) != None]
  for each in range(len(data)):
    if data[each].Result == "SLRUM_FAILED_QUEUE":
      data[each].Result = "C_FAILED"
  return render (request, 'main/testcase.html', {'testcase' : data, 'timestamp': timestamp})


"""
Search Data

autocomplete_(request, num)           : submenu.html       (autocomplete function on html textbox)
search_list(request, test_name, num)  : search_list.html   (Retrieve and render the entered data)
search_case(request, test_name, num)  : search_case.html   (Retrieve and render the entered data)
"""

def autocomplete_list(request, num):
  term = request.GET.get('term')
  results = models.TestList.objects.filter(Project_id=num, ListName__icontains=term).values('ListName')
  data = list(results)
  return JsonResponse(data, safe=False)

def autocomplete_case(request, num):
  term = request.GET.get('term')
  results = models.TestCase.objects.filter(TestList__Project_id=num, CaseName__icontains=term).values('CaseName')
  data = list(results)
  return JsonResponse(data, safe=False)

def search_list(request, test_name, num):
  project_name = models.Project.objects.get(pk=num)
  testlists = models.TestList.objects.filter(Project_id=num, ListName__icontains=test_name).order_by('ListName')
  testcases = models.TestCase.objects.filter(TestList__in=testlists)
  testcase_details = models.TestCase_Detail.objects.filter(TestCase__in=testcases).order_by('-BuildDate')
  context = {
    'project' : project_name,
    'testlists' : testlists,
    'testcases' : testcases,
    'testcase_details' : testcase_details,
    'timestamp' : timestamp
  }
  return render (request, 'main/search_list.html', context)

def search_case(request, test_name, num):
  project_name = models.Project.objects.get(pk=num)
  testcases = models.TestCase.objects.filter(TestList__Project_id=num, CaseName__icontains=test_name).order_by('CaseName')
  testcase_details = models.TestCase_Detail.objects.filter(TestCase__in=testcases).order_by('-BuildDate')
  context = {
    'project' : project_name,
    'testcases' : testcases,
    'testcase_details' : testcase_details,
    'timestamp' : timestamp
  }
  return render (request, 'main/search_case.html', context)