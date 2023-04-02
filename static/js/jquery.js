// This is the jQuery file for the Online Ticket System

$(document).ready(function() {
  // Code to handle the click event for the purchase button
  $('#purchase-button').click(function(event) {
    event.preventDefault();

    const ticketId = $(this).data('ticket-id');

    // Send an AJAX request to purchase the ticket
    $.ajax({
      type: 'POST',
      url: '/api/tickets',
      data: JSON.stringify({ticket_id: ticketId}),
      contentType: 'application/json',
      success: function(response) {
        // Show a success message
        showSuccessMessage('Ticket purchased successfully');
      },
      error: function(jqXHR, textStatus, errorThrown) {
        // Show an error message
        showErrorMessage(jqXHR.responseJSON.message);
      }
    });
  });
});

