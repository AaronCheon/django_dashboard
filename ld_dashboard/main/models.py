from django.db import models
import datetime
from django import forms
from django.utils import timezone

# Create your models here.
class Project(models.Model):
  ProjectName                = models.TextField(unique=True, null=False, blank=False)
  Completed                  = models.BooleanField(null=False, default=False)
  StartDate                  = models.DateTimeField(blank=False, null=False, default=timezone.now)
  EndDate                    = models.DateTimeField(blank=True, null=True)
  User_List                  = models.TextField(null=True, blank=True)

  def __str__(self):
    return f"Project({self.ProjectName})"

class TestList(models.Model):
  Project                    = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name="testlist")
  ListName                   = models.TextField(blank=False, null=False)
  Used                       = models.BooleanField(null=False, default=False)
  DutName                    = models.TextField(blank=False, null=False, default="FULL")

  def __str__(self):
    return f"{self.Project.ProjectName}.{self.ListName}"

  def latest(self):
    testcases = self.testcase.filter(Used=1)
    passed = failed = running = pending = 0
    for each in testcases:
      result = each.latest().Result
      if result == "PASSED":
        passed +=1
      elif result == "RUNNING" :
        running +=1
      elif result == "PENDING" :
        pending +=1
      else:
        failed +=1
    return (passed, failed, running, pending)

  def previous(self, date):
    testcases = self.testcase.all()
    passed = failed = running = pending = 0
    for each in [ each.previous(date).Result for each in testcases if each.previous(date) != None ]:
      if each == "PASSED":
        passed +=1
      elif each == "RUNNING" :
        running +=1
      elif each == "PENDING" :
        pending +=1
      else:
        failed +=1
    return (passed, failed, running, pending)

class TestCase(models.Model):
  TestList                   = models.ForeignKey(TestList, on_delete=models.DO_NOTHING, related_name="testcase")
  CaseName                   = models.TextField(blank=False, null=False)
  Used                       = models.BooleanField(null=False, default=False)

  class Meta:
    unique_together = ('CaseName', 'TestList')

  def __str__(self):
    return f"{self.TestList.ListName}.{self.CaseName}"
  def latest(self):
    temp = self.testcase_detail.filter(Canceled=0).last()
    return temp
  def previous(self, date):
    temp = self.testcase_detail.filter(BuildDate=date).last()
    return temp
class TestCase_Detail(models.Model):
  TestCase                   = models.ForeignKey(TestCase, on_delete=models.DO_NOTHING, related_name="testcase_detail")
  Result                     = models.TextField(blank=False, null=False, choices=[('PASSED', 'PASSED'), ('FAILED', 'FAILED'), ('RUNNING', 'RUNNING'),('PENDING', 'PENDING'),('SLRUM_FAILED', 'SLRUM_FAILED'),('C_FAILED', 'C_FAILED'),('SLRUM_FAILED_QUEUE','SLRUM_FAILED_QUEUE')], default='PENDING')
  Command                    = models.TextField(blank=True, null=True)
  StartDate                  = models.DateTimeField(blank=True, null=True)
  EndDate                    = models.DateTimeField(blank=True, null=True)
  SimPath                    = models.TextField(blank=True, null=True)
  Commit                     = models.TextField(blank=True, null=True)
  Canceled                   = models.BooleanField(null=False, default=False)
  BuildDate                  = models.DateField(blank=True, null=True)

class WeeklyTable(models.Model):
  Total                      = models.IntegerField(blank=False, null=False)
  Passed                     = models.IntegerField(blank=False, null=False)
  Failed                     = models.IntegerField(blank=False, null=False)
  datetime                   = models.DateField(blank=False, null=False, default=timezone.now)
  ProjectName                = models.TextField(null=False, blank=False)
  commit                     = models.TextField(null=True, blank=True)