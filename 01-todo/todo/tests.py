from django.test import TestCase
from django.urls import reverse
from .models import Todo
from datetime import date

class TodoModelTest(TestCase):
    def test_string_representation(self):
        todo = Todo(title="My Test Task")
        self.assertEqual(str(todo), "My Test Task")

    def test_default_values(self):
        todo = Todo.objects.create(title="Defaults Task")
        self.assertFalse(todo.is_resolved)
        self.assertIsNone(todo.due_date)

class TodoViewTest(TestCase):
    def setUp(self):
        self.todo = Todo.objects.create(
            title="Existing Task",
            description="Test Description",
            due_date=date(2025, 12, 31)
        )

    def test_todo_list_view(self):
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/todo_list.html')
        self.assertContains(response, "Existing Task")

    def test_todo_create_view(self):
        response = self.client.post(reverse('todo_create'), {
            'title': 'New Task',
            'description': 'New Description',
            'due_date': '2025-01-01',
            'is_resolved': False
        })
        self.assertEqual(response.status_code, 302)  # Redirects to list
        self.assertEqual(Todo.objects.count(), 2)
        self.assertTrue(Todo.objects.filter(title='New Task').exists())

    def test_todo_update_view(self):
        response = self.client.post(reverse('todo_update', args=[self.todo.pk]), {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'due_date': '2025-12-31',
            'is_resolved': True
        })
        self.assertEqual(response.status_code, 302)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Task')
        self.assertTrue(self.todo.is_resolved)

    def test_todo_delete_view(self):
        response = self.client.post(reverse('todo_delete', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Todo.objects.count(), 0)

    def test_create_invalid_input(self):
        # Title is required, so sending empty title should fail
        response = self.client.post(reverse('todo_create'), {
            'title': '',
            'description': 'Fail'
        })
        self.assertEqual(response.status_code, 200)  # Re-renders form
        
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('title', form.errors)
        self.assertEqual(form.errors['title'], ['This field is required.'])
        
        self.assertEqual(Todo.objects.count(), 1)

    def test_update_404(self):
        response = self.client.get(reverse('todo_update', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_404(self):
        response = self.client.get(reverse('todo_delete', args=[999]))
        self.assertEqual(response.status_code, 404)
