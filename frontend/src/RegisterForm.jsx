function RegisterForm() {
  const handleSubmit = async (e) => {
    e.preventDefault();
    // 這裡可以加上註冊邏輯

    const requestInfo = {
      url: 'http://localhost:5001/api/auth/register',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: e.target.username.value,
        password: e.target.password.value,
      }),
    };

    const response = await fetch(requestInfo.url, requestInfo);
    if(response.ok) {
      // console.log('Registration successful');
      response.json().then(data => {
        // console.log('Registration successful:', data);
      });
      alert('Registration successful');
      return window.location.href = '/login';
    }
    alert('Registration failed, please try again later');
  }


  return (
    <div>
      <h1>Register</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="username">Username</label>
        <input name="username" id="username" required />
        <label htmlFor="password">Password</label>
        <input type="password" name="password" id="password" required />
        <input type="submit" value="Register" />
      </form>
    </div>
  );
}

export default RegisterForm;
