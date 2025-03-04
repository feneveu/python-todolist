from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Sample task list
tasks = []

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        task = request.form.get('task')
        if task:
            tasks.append(task)  # Add task to the list
        return redirect(url_for('index'))
    return render_template('add_task.html')

if __name__ == '__main__':
    app.run(debug=True)
