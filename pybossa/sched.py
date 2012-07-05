# This file is part of PyBOSSA.
# 
# PyBOSSA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PyBOSSA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with PyBOSSA.  If not, see <http://www.gnu.org/licenses/>.

#import json
#from flask import Blueprint, request, url_for, flash, redirect, abort
#from flask import abort, request, make_response, current_app
import pybossa.model as model
import random

def get_task(app_id, user_id=None, user_ip=None, n_answers=30):
    """Gets a new task for a given application"""
    # Get all pending tasks for the application
    tasks = model.Session.query(model.Task)\
            .filter(model.Task.app_id==app_id)\
            .filter(model.Task.state!="completed")\
            .all()

    # Update state of uncompleted tasks if the len(TaskRuns) >= n_answers
    for t in tasks:
        if (t.info.get('n_answers')):
            n_answers = t.info['n_answers']
        if (len(t.task_runs) >= n_answers):
                t.state = "completed"
                model.Session.merge(t)
                model.Session.commit()

    # Get all pending tasks again after the update
    tasks = model.Session.query(model.Task)\
            .filter(model.Task.app_id==app_id)\
            .filter(model.Task.state!="completed")

    # Create a list of candidate_tasks
    candidate_tasks = []
    if user_id and not user_ip:
        #print "Authenticated user"
        for t in tasks:
            n = model.Session.query(model.TaskRun)\
                    .filter(model.TaskRun.app_id==app_id)\
                    .filter(model.TaskRun.task_id==t.id)\
                    .filter(model.TaskRun.user_id==user_id)\
                    .count()
            # The user has not participated in this task
            if n == 0:
                candidate_tasks.append(t)
    else:
        #print "Anonymous user"
        if not user_ip:
            user_ip = "127.0.0.1"
        for t in tasks:
            n = model.Session.query(model.TaskRun)\
                        .filter(model.TaskRun.app_id==app_id)\
                        .filter(model.TaskRun.task_id==t.id)\
                        .filter(model.TaskRun.user_ip==user_ip)\
                        .count()
                # The user has not participated in this task
            if n == 0:
                candidate_tasks.append(t)
    
    total_remaining = len(candidate_tasks)
    if total_remaining == 0:
        return None
    rand = random.randrange(0, total_remaining)
    out = candidate_tasks[rand]
    return out