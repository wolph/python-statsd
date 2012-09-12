from __future__ import with_statement
import mock
import statsd

with mock.patch('statsd.Client') as mock_client:
    instance = mock_client.return_value
    instance._send.return_value = 1

    # Some simple decorator tests
    timer0 = statsd.Timer('timer0')
    @timer0.decorate
    def a():
        pass
    a()
    mock_client._send.assert_called_with(mock.ANY, {'timer0.a': '0|ms'})


    timer1 = statsd.Timer('timer1')
    @timer1.decorate('spam')
    def b():
        pass
    b()
    mock_client._send.assert_called_with(mock.ANY, {'timer1.spam': '0|ms'})


    timer2 = timer1.get_client('eggs')
    @timer2.decorate
    def c():
        pass
    c()
    mock_client._send.assert_called_with(mock.ANY, {'timer1.eggs.c': '0|ms'})


    timer3 = timer1.get_client('eggs0')
    @timer3.decorate('d0')
    def d():
        pass
    d()
    mock_client._send.assert_called_with(mock.ANY, {'timer1.eggs0.d0': '0|ms'})



    # More advanced usage with intermediate timers
    timer4 = statsd.Timer('timer4')
    timer4.start()
    timer4.stop()
    mock_client._send.assert_called_with(mock.ANY, {'timer4.total': '0|ms'})


    timer5 = statsd.Timer('timer5')
    timer5.start()
    timer5.stop('test')
    mock_client._send.assert_called_with(mock.ANY, {'timer5.test': '0|ms'})


    timer6 = statsd.Timer('timer6')
    timer6.start()
    timer6.intermediate('extras')
    mock_client._send.assert_called_with(mock.ANY, {'timer6.extras': '0|ms'})
    timer6.stop()
    mock_client._send.assert_called_with(mock.ANY, {'timer6.total': '0|ms'})


    timer7 = statsd.Timer('timer7')
    timer7.start()
    timer7.intermediate('extras')
    mock_client._send.assert_called_with(mock.ANY, {'timer7.extras': '0|ms'})
    timer7.stop('test')
    mock_client._send.assert_called_with(mock.ANY, {'timer7.test': '0|ms'})

