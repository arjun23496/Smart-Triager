function sanitize_json(x)
{
	x = x.replace(/u/g,'')
	x = x.replace(/'/g,'"')
	x = JSON.parse(x)

	return x	
}