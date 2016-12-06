# -*- coding: utf-8 -*-

def make_response(data={}, message="ok", current_page=1, status=1):
	return {
		"data": data, "message": message, "current_page": current_page, "status": status
	}