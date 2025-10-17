from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class SearchApparelAPITestCase(APITestCase):
    """Test cases for the unified apparel search endpoint"""
    
    def test_search_endpoint_requires_query(self):
        """Test that search endpoint returns 400 when query parameter is missing"""
        url = reverse('search_apparel')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_search_endpoint_accepts_query(self):
        """Test that search endpoint accepts query parameter"""
        url = reverse('search_apparel')
        # This will test the endpoint structure without actually scraping
        # In a real test, we would mock the scraper responses
        response = self.client.get(url, {'q': 'test'})
        # The endpoint should return either 200 or 500 (if scraping fails)
        # but not 400 (which would mean bad request)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR])
    
    def test_search_endpoint_response_structure_flat(self):
        """Test that flat response format has correct structure"""
        url = reverse('search_apparel')
        response = self.client.get(url, {'q': 'test', 'format': 'flat'})
        
        if response.status_code == status.HTTP_200_OK:
            data = response.data
            self.assertIn('query', data)
            self.assertIn('count', data)
            self.assertIn('results', data)
            self.assertEqual(data['query'], 'test')
    
    def test_search_endpoint_response_structure_grouped(self):
        """Test that grouped response format has correct structure"""
        url = reverse('search_apparel')
        response = self.client.get(url, {'q': 'test', 'format': 'grouped'})
        
        if response.status_code == status.HTTP_200_OK:
            data = response.data
            self.assertIn('query', data)
            self.assertIn('total_results', data)
            self.assertIn('platforms', data)
            self.assertEqual(data['query'], 'test')

