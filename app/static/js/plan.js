// plan.js
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('add-requirement').addEventListener('click', function() {
      var requirementsList = document.getElementById('requirements-list');
      var newRequirement = document.createElement('div');
      newRequirement.classList.add('form-group');
      newRequirement.innerHTML = '<input type="text" name="requirements-' + requirementsList.childElementCount + '-requirement" class="form-control" required>';
      requirementsList.appendChild(newRequirement);
    });
  
    document.getElementById('add-stage').addEventListener('click', function() {
      var timelineList = document.getElementById('timeline-list');
      var newStage = document.createElement('div');
      newStage.classList.add('form-group');
      newStage.innerHTML = '<input type="text" name="timeline" class="form-control" required>';
      timelineList.appendChild(newStage);
    });
  });