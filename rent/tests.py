from datetime import date

from django.test import TestCase, TransactionTestCase
from rest_framework import status
from rest_framework.reverse import reverse

from rent.models import Rental, Reservation


def get_rental():
    return Rental.objects.first()


class RentModelsTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        Rental.objects.create(name='Apartment 11')

    def test_create_rental(self):
        rental = get_rental()
        self.assertTrue(isinstance(rental, Rental))
        self.assertEqual(Rental.objects.count(), 1)
        self.assertEqual(Rental.objects.first().name, "Apartment 11")

    def test_create_reservation(self):
        rental = get_rental()
        reservation = Reservation.objects.create(checkin="2022-01-01", checkout="2022-01-02", rental=rental)
        self.assertTrue(isinstance(reservation, Reservation))
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(Reservation.objects.first().checkin, date(2022, 1, 1))


class RentViewsTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self) -> None:
        rental1 = Rental.objects.create(name='rental-1')
        rental2 = Rental.objects.create(name='rental-2')

        Reservation.objects.create(checkin="2022-01-01", checkout="2022-01-13", rental=rental1)
        Reservation.objects.create(checkin="2022-01-20", checkout="2022-02-10", rental=rental1)
        Reservation.objects.create(checkin="2022-02-20", checkout="2022-03-10", rental=rental1)

        Reservation.objects.create(checkin="2022-01-02", checkout="2022-01-20", rental=rental2)
        Reservation.objects.create(checkin="2022-01-20", checkout="2022-02-11", rental=rental2)

    # rental
    def test_rental_viewset_list(self):
        rental = get_rental()
        url = reverse('rentals')
        result = self.client.get(url)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertIn(rental.name, result.json()[0]['name'])

    def test_rental_viewset_create(self):
        url = reverse('rentals')
        data = {"name": "Large Mansion 1"}
        result = self.client.post(url, data=data)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rental.objects.count(), 3)
        self.assertEqual(Rental.objects.last().name, "Large Mansion 1")

    def test_rental_viewset_get_success(self):
        rental = get_rental()
        url = reverse('rental', kwargs={"pk": rental.id})
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.json()["id"], rental.id)

    def test_rental_viewset_get_fail(self):
        url = reverse('rental', kwargs={"pk": 69})
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)

    def test_rental_viewset_destroy(self):
        rental = get_rental()
        url = reverse('rental', kwargs={"pk": rental.id})
        result = self.client.delete(url)
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)

    # reservation
    def test_reservation_viewset_list_default_pagination(self):
        # main feature of the assignment

        expected_result = [{'rental_name': 'rental-1', 'id': 1, 'checkin': '2022-01-01', 'checkout': '2022-01-13',
                            'previous_reservation': None},
                           {'rental_name': 'rental-1', 'id': 2, 'checkin': '2022-01-20', 'checkout': '2022-02-10',
                            'previous_reservation': 1},
                           {'rental_name': 'rental-1', 'id': 3, 'checkin': '2022-02-20', 'checkout': '2022-03-10',
                            'previous_reservation': 2},
                           {'rental_name': 'rental-2', 'id': 4, 'checkin': '2022-01-02', 'checkout': '2022-01-20',
                            'previous_reservation': None},
                           {'rental_name': 'rental-2', 'id': 5, 'checkin': '2022-01-20', 'checkout': '2022-02-11',
                            'previous_reservation': 4}]

        url = reverse('reservations')
        result = self.client.get(url)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.json()['results'], expected_result)

    def test_reservation_viewset_list_custom_pagination(self):
        expected_result = [{'rental_name': 'rental-1', 'id': 1, 'checkin': '2022-01-01', 'checkout': '2022-01-13',
                            'previous_reservation': None},
                           {'rental_name': 'rental-1', 'id': 2, 'checkin': '2022-01-20', 'checkout': '2022-02-10',
                            'previous_reservation': 1}]

        url = reverse('reservations') + '?page=1&page_size=2'
        result = self.client.get(url)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.json()['results'], expected_result)

    def test_reservation_viewset_create_success(self):
        rental = get_rental()
        url = reverse('reservations')
        data = {"rental": rental.id, "checkin": "2022-06-06", "checkout": "2022-06-12"}
        result = self.client.post(url, data=data)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 6)
        self.assertEqual(Reservation.objects.last().checkout, date(2022, 6, 12))

    def test_reservation_viewset_create_checkout_before_checkin_fail(self):
        rental = get_rental()
        url = reverse('reservations')
        data = {"rental": rental.id, "checkin": "2022-06-12", "checkout": "2022-06-06"}
        result = self.client.post(url, data=data)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Reservation.objects.count(), 5)

    def test_reservation_viewset_create_busy_date_fail(self):
        rental = get_rental()
        existing_reservation = Reservation.objects.last()
        url = reverse('reservations')
        data = {"rental": rental.id, "checkin": existing_reservation.checkin, "checkout": existing_reservation.checkout}
        result = self.client.post(url, data=data)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Reservation.objects.count(), 5)

    def test_reservation_viewset_destroy(self):
        existing_reservation = Reservation.objects.last()
        url = reverse('reservation', kwargs={"pk": existing_reservation.id})
        result = self.client.delete(url)
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)

    def test_reservation_viewset_update(self):
        existing_reservation = Reservation.objects.last()
        data = {
            "rental": existing_reservation.rental_id,
            "checkin": "2022-12-31",
            "checkout": "2023-01-01",
        }
        expected_result = {
            "id": existing_reservation.id,
            **data
        }
        url = reverse('reservation', kwargs={"pk": existing_reservation.id})
        result = self.client.put(url, data=data, content_type='application/json')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.json(), expected_result)
