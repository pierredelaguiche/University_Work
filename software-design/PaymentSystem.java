package leipflix;

public class PaymentSystem implements PaymentInterface{
	
	public void performPayment() {
		System.out.println("Asking payment details...");
		System.out.println("Validating payment...");
		System.out.println("Payment went through!");
	}
}
