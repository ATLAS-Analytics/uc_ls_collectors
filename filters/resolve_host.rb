require 'socket'

def lookup_hostname(ip)
    client => ''   
    begin
        client = Socket.gethostbyaddr(IPAddr.new(ip).hton).first
    rescue SocketError
    end
    return client
end

def filter(event)
    
    event.set("client", lookup_hostname(event.get("ip")) ) unless event.get("client")

    return [event]
end