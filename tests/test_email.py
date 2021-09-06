import pytest


class TestTemplateView:

    @pytest.mark.skip
    @pytest.mark.django_db(transaction=True)
    def test_reset_password_email(self, user, client):
        reset_url = '/auth/password_reset/'

        data = {
            'email': user.email
        }
        response = client.post(reset_url, )

        # TODO assert redirect
        assert response.status_code in (301, 302, ), (
            'fdfdf'
        )

        # TODO Assert redirect to /auth/password_reset/done/ with 200

        # TODO check email in sent emails. Add temp dir
