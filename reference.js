const guests = ['1 Guest', '2 Guests', '3 Guests', '4 Guests', '5 Guests+'];

const SelectGuest = () => {
	return (
		<select>
			{guests.map((guest, index) => {
				return <option key={index}>{guest}</option>
			})}
	</select>
	)
}

const SelectRoomType = () => {
	return (
		<select>
			<option>Entire Place</option>
			<option>Private Room</option>
			<option>Shared Room</option>
	</select>
	)
}

const RequestForm = (props) => {
	return (
		<form className="request-form" onSubmit={props.handleSubmit}>
			<input type="text" placeholder="Enter Location" required/>
			<SelectGuest/>
			<SelectRoomType/>
			{props.calculatedEarning ? (
				<p className="calculated-earnings">${props.calculatedEarning}
					<span class="note">monthly potential</span>
				</p>
			):(
				''
			)}
			<input type="submit" value="Get Started"/>
	</form>
	)
}

class Card extends React.Component {
	state = {
		calculatedEarning: ''
	}
	handleSubmit = (e) => {
		e.preventDefault();
		const price = Math.floor(Math.random() * Math.floor(10000));
		this.setState({
			calculatedEarning: price
		})
	}
	render(){
		return (
		<div className="card">
			<h3>Find out what top hosts earn in your area</h3>
			<RequestForm handleSubmit={this.handleSubmit} calculatedEarning={this.state.calculatedEarning}/>
		</div>
	)	
	}
}

ReactDOM.render(<Card />, document.getElementById('root'))
