from mozilla_django_oidc.auth import OIDCAuthenticationBackend
import logging, my_config
from django.shortcuts import redirect


class MyOIDCAB(OIDCAuthenticationBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jwt_decoded = None

    # -----------------------------------------------------------------------
    def _decode_jwt(self, token):
        import jwt
        jwks_client = jwt.PyJWKClient(my_config.OIDC_OP_JWKS_ENDPOINT)
        try:
            key = jwks_client.get_signing_key_from_jwt(token).key
        except Exception as ex:
            logging.error(f"[TokenVerifier] Failed to get signing key: {ex}")
            return None

        jwt_decoded = jwt.decode(jwt=token, key=key, algorithms=["RS256"], audience=my_config.OIDC_AUDIENCE)
        print(f"===> JWT {jwt_decoded}")
        return jwt_decoded            

    # -----------------------------------------------------------------------
    def _get_userinfo(self, access_token ):
        headers = {
            "Authorization": f"Bearer {access_token}",
            #"Accept": "application/json"
        }
        response = ""
        try:
            response = requests.get(my_config.OIDC_OP_USER_ENDPOINT , headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes

            user_data = response.json()
            user_groups = user_data.get("groups", []) # Common key, adjust as needed
            if (user_groups):
                print(f"groups: {user_groups}")
                
            return user_data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user info: {e} : {response} {response.text}")
        except ValueError:
            print("Error decoding JSON response.")
            
        return None

    def _verify_group_membership(self, jwt_decoded=None):
        if ( not jwt_decoded):
            return True

        scopes = my_config.OIDC_RP_SCOPES.split()
        is_in_group = True
        for s in scopes:
            if not s.startswith("group:"):
                continue
            is_in_group = s in jwt_decoded.get("scope", "")
            if ( is_in_group):
                print(f"Passed membership test in groups ===> {s} " )
            else:
                print(f"Failed membership test in groups ===> {s} " )

        return is_in_group

    def _verify_claims(self, claims):
        verified = super(MyOIDCAB, self).verify_claims(claims)
        print(f"CLAIMS: {claims}")
        is_in_group= self.verify_group_membership()
        return verified and is_in_group

    def authenticate(self, request, **kwargs):
        ret = super().authenticate(request, **kwargs)
        access_token = self.request.session.get('oidc_access_token','None check: OIDC_STORE_ACCESS_TOKEN')
        jwt_decoded = self._decode_jwt(access_token)
        member = True
        member = self._verify_group_membership(jwt_decoded)
        print(f"ACCESS TOKEN: {access_token} {ret} {member}")

        if ( not member):
            return None
        return ret
        
