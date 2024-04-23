EMAIL_HTML_TEMPLATE = """
<html>
	<head></head>
	<body>
		<p>Hello, {}!</p>
		<p>We are happy that you use our application.</p>
    <p>
			This verification code can be used at any time unless you request another one.
			In this case it will lose validity and only the most recent one will be valid.
    </p>
		<section class="code">
			<p>Verification code:</h2>
			<p>{}</p>
		</section>
    <p class="bye">Bye!</p>
	</body>
</html>
"""